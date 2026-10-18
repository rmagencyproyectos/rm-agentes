#!/usr/bin/env bash
# Check-in diario de Winston (Winy) — lo dispara launchd de madrugada.
#
# Reparto de trabajo: Python recoge el estado (0 tokens), UNA llamada a Haiku sin herramientas
# le pone la voz, y bash lo envía con notify.sh. El modelo ya no explora archivos ni ejecuta
# nada, así que no hay bucle agéntico: 1 turno y listo.
#   winston-checkin.sh            -> redacta y envía
#   winston-checkin.sh --dry-run  -> redacta y lo imprime, sin enviar
# Requisitos: `claude setup-token` hecho una vez (token de larga duración).
set -uo pipefail

export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
WIN="$HUB/infra/winston"
LOG="$WIN/last-run.log"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

cd "$HUB" || exit 1

# Token de larga duración para modo desatendido (gitignored). Lo genera `claude setup-token`.
[ -f "$HUB/infra/.env.winston" ] && { set -a; . "$HUB/infra/.env.winston"; set +a; }

{ echo ""; echo "===== $(date '+%Y-%m-%d %H:%M') · Winston check-in ====="; } >> "$LOG"

# --- 1. Estado del sistema (Python puro, 0 tokens). Refrescamos la cobertura: es de
#        madrugada y da igual tardar unos segundos, así el dato sale fresco. ---
ESTADO=$(python3 "$HUB/infra/estado/estado.py" --refrescar 2>>"$LOG")
if [ -z "$ESTADO" ]; then
  echo "  [error] no pude recoger el estado; aborto" >> "$LOG"
  echo "exit=1 ($(date '+%H:%M'))" >> "$LOG"
  exit 1
fi

# --- 2. Una sola llamada al modelo: solo redacta. Sin herramientas, sin turnos extra. ---
#
# ⚠️ El tope de coste NO es cosmético: del 10 al 13/08/2026 el check-in murió cuatro noches
# seguidas con `error_max_budget_usd` porque estaba en 0.05 y el coste real había ido subiendo
# (0.048 → 0.093) según crecía el estado. Como el envío solo ocurre si el modelo responde,
# el fallo era invisible: Gerard seguía recibiendo cobertura y guiones, que son otros scripts.
# Si vuelves a tocarlo, deja holgura y NO lo bajes al coste observado: el estado crece solo.
TMP_JSON="$WIN/tmp-checkin-$$.json"
trap 'rm -f "$TMP_JSON"' EXIT

printf 'ESTADO DEL SISTEMA (hoy):\n%s\n' "$ESTADO" | claude -p \
  --model claude-haiku-4-5-20251001 \
  --tools "" \
  --disable-slash-commands \
  --no-session-persistence \
  --system-prompt "$(cat "$WIN/winston-voz.md")" \
  --max-budget-usd 0.20 \
  --output-format json > "$TMP_JSON" 2>>"$LOG"

MSG=$(python3 - "$TMP_JSON" <<'PY' 2>>"$LOG"
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    sys.stderr.write("  [error] respuesta ilegible (%s)\n" % e)
    sys.exit(1)
u = d.get("usage") or {}
# Con caché de prompt, `input_tokens` solo cuenta lo que no venía de la caché: hay que sumar.
ent = sum((it.get("input_tokens") or 0) + (it.get("cache_read_input_tokens") or 0)
          + (it.get("cache_creation_input_tokens") or 0)
          for it in (u.get("iterations") or [])) or (u.get("input_tokens") or 0)
sys.stderr.write("  [uso] turnos=%s entrada_total=%s salida=%s coste=%s\n" % (
    d.get("num_turns"), ent, u.get("output_tokens"), d.get("total_cost_usd")))
if d.get("is_error") or d.get("subtype") != "success":
    sys.stderr.write("  [error] subtype=%s :: %s\n" % (d.get("subtype"), d.get("result")))
    sys.exit(1)
r = (d.get("result") or "").strip()
if not r:
    sys.stderr.write("  [error] mensaje vacío\n")
    sys.exit(1)
sys.stdout.write(r)
PY
)
rc=$?

# Si el modelo no responde (tope de coste, red, token caducado), NO se calla: se manda el
# estado en crudo con una cabecera de aviso. Un check-in feo llega; uno que no llega no se
# nota, y así es como estuvimos cuatro noches sin saberlo.
if [ "$rc" != "0" ] || [ -z "$MSG" ]; then
  echo "  [error] el modelo no devolvió mensaje; mando el estado en crudo" >> "$LOG"
  if [ "$DRY" = "1" ]; then
    printf '\n--- [DRY RUN] fallo del modelo: se enviaría el estado en crudo ---\n%s\n---\n' "$ESTADO"
    echo "exit=1 (dry-run, modelo caído, $(date '+%H:%M'))" >> "$LOG"
    exit 1
  fi
  CRUDO=$(printf '⚠️ *El check-in de hoy va en crudo* — no he podido redactarlo (mira %s).\nTe paso el estado tal cual:\n\n%s' "$LOG" "$ESTADO")
  "$HUB/infra/notifier/notify.sh" "$CRUDO" DIGEST_CICLO alta >> "$LOG" 2>&1
  echo "  envío crudo: notify.sh exit=$?" >> "$LOG"
  echo "exit=1 ($(date '+%H:%M'))" >> "$LOG"
  exit 1
fi

# Markdown -> formato WhatsApp (negrita con UN asterisco)
MSG=$(printf '%s' "$MSG" | python3 "$HUB/infra/formato_wa.py" 2>>"$LOG" || printf '%s' "$MSG")

# --- 3. Enviar (lo hace bash, no el modelo) ---
if [ "$DRY" = "1" ]; then
  printf '\n--- [DRY RUN] se enviaría por WhatsApp ---\n%s\n---\n' "$MSG"
  echo "exit=0 (dry-run, $(date '+%H:%M'))" >> "$LOG"
  exit 0
fi

"$HUB/infra/notifier/notify.sh" "$MSG" DIGEST_CICLO normal >> "$LOG" 2>&1
envio=$?
echo "  envío: notify.sh exit=$envio" >> "$LOG"

echo "exit=0 ($(date '+%H:%M'))" >> "$LOG"
exit 0
