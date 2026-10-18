#!/usr/bin/env bash
# Procesa UN mensaje entrante de Gerard: si es audio lo transcribe, mete la memoria de los
# últimos 30 días, corre Winy (Claude headless con permiso para ejecutar tareas) y responde
# por WhatsApp. Lo invoca webhook.py.
#   process.sh "<texto>"                -> mensaje de texto
#   process.sh __AUDIO__ "<message_id>" -> nota de voz (se descarga y transcribe)
set -uo pipefail

export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
VAULT="/Users/gerardruizmiro/rmagency"   # vault de Obsidian: aquí viven las notas de Gerard
RESP="$HUB/infra/responder"
LOG="$RESP/responder.log"
API="http://127.0.0.1:8080"
MARK=$'\xe2\x80\x8b'   # zero-width space: marca invisible de "mensaje de la Winy" (anti-bucle)

cd "$HUB" || exit 1
[ -f "$HUB/infra/.env.winston" ] && { set -a; . "$HUB/infra/.env.winston"; set +a; }
set -a; . "$HUB/infra/.env"; set +a

# --- Enviar un texto por WhatsApp (con marca invisible) y registrar id anti-bucle ---
# Con WINY_DRY_RUN=1 no envía nada: lo imprime. Sirve para probar el flujo sin dar la brasa.
wa_reply() {
  local out payload resp id
  if [ "${WINY_DRY_RUN:-0}" = "1" ]; then
    printf '\n--- [DRY RUN] se enviaría por WhatsApp ---\n%s\n---\n' "$1"
    return 0
  fi
  out="${1}${MARK}"
  payload=$(NUM="$WA_DESTINO" TXT="$out" python3 -c 'import json,os;print(json.dumps({"number":os.environ["NUM"],"text":os.environ["TXT"]}))')
  resp=$(curl -s --max-time 15 -X POST -H "apikey: $AUTHENTICATION_API_KEY" \
    -H "Content-Type: application/json" "$API/message/sendText/$WA_INSTANCE" \
    -d "$payload" 2>/dev/null || echo "")
  id=$(printf '%s' "$resp" | python3 -c "import sys,json;print((json.load(sys.stdin).get('key') or {}).get('id',''))" 2>/dev/null || echo "")
  [ -n "$id" ] && echo "$id" >> "$RESP/sent-ids.log"
}

USER_MSG="${1:-}"
[ -z "$USER_MSG" ] && exit 0

# --- Si es audio: descargar de Evolution y transcribir ---
if [ "$USER_MSG" = "__AUDIO__" ]; then
  MID="${2:-}"
  { echo ""; echo "===== $(date '+%F %T') · IN(audio): $MID"; } >> "$LOG"
  body=$(M="$MID" python3 -c 'import json,os;print(json.dumps({"message":{"key":{"id":os.environ["M"]}}}))')
  b64=$(curl -s --max-time 25 -X POST -H "apikey: $AUTHENTICATION_API_KEY" \
    -H "Content-Type: application/json" "$API/chat/getBase64FromMediaMessage/$WA_INSTANCE" \
    -d "$body" 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('base64','') or '')" 2>/dev/null || echo "")
  if [ -z "$b64" ]; then
    wa_reply "Te llegó un audio pero no pude descargarlo 😅 ¿me lo escribes en texto?"
    echo "  -> fallo descarga audio" >> "$LOG"; exit 0
  fi
  tmp="$RESP/tmp-audio-$$.ogg"
  printf '%s' "$b64" | base64 -d > "$tmp" 2>/dev/null
  USER_MSG=$(python3 "$RESP/transcribe.py" "$tmp" 2>>"$LOG"); rc=$?
  rm -f "$tmp"
  if [ "$rc" = "2" ]; then
    wa_reply "Te escuché pero aún no tengo activada la transcripción de audios 🎧 Escríbeme en texto de momento."
    echo "  -> sin ASSEMBLYAI_API_KEY" >> "$LOG"; exit 0
  fi
  if [ "$rc" != "0" ] || [ -z "$USER_MSG" ]; then
    wa_reply "Te escuché pero no pude entender el audio (rc=$rc) 😅 ¿me lo repites o me lo escribes?"
    echo "  -> transcripción falló rc=$rc" >> "$LOG"; exit 0
  fi
  echo "  -> transcrito: $USER_MSG" >> "$LOG"
fi

{ echo ""; echo "===== $(date '+%F %T') · IN: $USER_MSG"; } >> "$LOG"

# Guarda el intercambio en la memoria de 30 días. Solo se llama cuando la respuesta es
# BUENA: si guardáramos también los errores, un "You've hit your session limit" quedaría
# grabado como respuesta de Winy y se le reinyectaría en cada mensaje siguiente.
guardar_memoria() {
  [ "${WINY_DRY_RUN:-0}" = "1" ] && return 0
  printf '%s' "$USER_MSG" | python3 "$RESP/memoria.py" add gerard
  printf '%s' "$1"        | python3 "$RESP/memoria.py" add winy
}

# --- ¿Gerard manda un link de Instagram/TikTok? Es una referencia para una idea: se recogen
# los metadatos (sin descargar el vídeo) y se fuerza el carril 2 para guardarla en Notion. ---
LINK_URL=$(printf '%s' "$USER_MSG" | python3 -c "import sys,re;m=re.search(r'https?://\S*(?:instagram\.com|tiktok\.com)\S*', sys.stdin.read(), re.I);print(m.group(0) if m else '')" 2>/dev/null)
LINK_INFO=""
if [ -n "$LINK_URL" ]; then
  echo "  -> link detectado: $LINK_URL" >> "$LOG"
  LINK_INFO=$(python3 "$HUB/infra/ideas/video_link.py" "$LINK_URL" 2>>"$LOG" || echo "")
fi

# =====================================================================================
# CARRIL 0 — consultas con respuesta calculable (cobertura, estado, ayuda). 0 tokens.
# (Si hay link, no es una consulta: se salta directo al carril 2.)
# =====================================================================================
if [ -z "$LINK_URL" ] && reply=$(python3 "$HUB/infra/estado/router.py" "$USER_MSG" 2>>"$LOG"); then
  wa_reply "$reply"
  guardar_memoria "$reply"
  { echo "OUT(carril 0 · 0 tokens): $reply"; } >> "$LOG"
  exit 0
fi

# =====================================================================================
# CARRIL 0.5 — acción "guioniza ya" (URGENCIA). 0 tokens, sin modelo: bash dispara el script.
# Ej.: "guioniza ya la de Golossa". Reparte + guioniza al momento (no espera a la madrugada).
# Corre en bash normal (no es el `claude -p` con gate), así que SÍ puede ejecutar el script.
# =====================================================================================
if [ -z "$LINK_URL" ]; then
  GY=$(python3 "$HUB/infra/notion/parse_guioniza.py" "$USER_MSG" 2>>"$LOG")
  if [ -n "$GY" ]; then
    LBL="$GY"; [ "$GY" = "ALL" ] && LBL="todos los pendientes"
    echo "  -> carril 0.5 (guioniza ya): $GY" >> "$LOG"
    wa_reply "⚡ Marchando, guionizo $LBL… te aviso en cuanto esté (tarda ~1 min)."
    if [ "$GY" = "ALL" ]; then
      OUT=$(bash "$HUB/infra/notion/guioniza-ya.sh" 2>&1)
    else
      OUT=$(bash "$HUB/infra/notion/guioniza-ya.sh" "$GY" 2>&1)
    fi
    rc=$?
    RES=$(printf '%s' "$OUT" | grep -E '^(✓|✗|Guionadas|Distribuidas|Nada|Notion|Falta)' | tail -n 8)
    [ -z "$RES" ] && RES="Hecho (rc=$rc). Míralo en 🎬 A grabar."
    wa_reply "⚡ Guioniza ya · $LBL:
$RES"
    guardar_memoria "$RES"
    echo "OUT(carril 0.5): rc=$rc" >> "$LOG"
    exit 0
  fi
fi

# --- Estado del sistema (Python puro): lo que antes el modelo iba a buscar con Glob/Read ---
ESTADO=$(python3 "$HUB/infra/estado/estado.py" 2>>"$LOG" || echo "(estado no disponible)")

# --- Memoria: hilo reciente, recortado ---
HISTORIAL=$(python3 "$RESP/memoria.py" render 2>/dev/null || echo "")

MENSAJE="ESTADO DEL SISTEMA (hoy):
$ESTADO

CONVERSACIÓN RECIENTE (contexto, NO lo repitas literal):
${HISTORIAL:-(sin conversaciones previas)}

MENSAJE DE GERARD (por WhatsApp, ahora):
$USER_MSG"

# Si venía un link de IG/TikTok, se lo damos ya masticado y le pedimos guardar la idea.
# El FORMATO (Reel/Carrusel) no lo decide el modelo: lo deduce video_link.py de la URL. Antes
# aquí iba "Reel" escrito a fuego en la plantilla y por eso TODO entraba como Reel.
if [ -n "$LINK_INFO" ]; then
  LINK_FORMATO=$(printf '%s' "$LINK_INFO" | python3 -c "import sys,json;print(json.load(sys.stdin).get('formato',''))" 2>/dev/null)
  [ -n "$LINK_FORMATO" ] && echo "  -> formato deducido del link: $LINK_FORMATO" >> "$LOG"
  if [ -n "$LINK_FORMATO" ]; then
    LINEA_FORMATO="  {\"idea\": \"<resumen corto>\", \"formato\": \"$LINK_FORMATO\", \"origen\": \"link IG/TikTok\", \"referencia\": \"$LINK_URL\"}
El \"formato\" ya viene deducido de la URL: cópialo tal cual. Solo cámbialo si Gerard dice en su
mensaje otra cosa explícitamente (\"este carrusel\", \"este reel\"); entonces manda lo que él diga."
  else
    LINEA_FORMATO="  {\"idea\": \"<resumen corto>\", \"origen\": \"link IG/TikTok\", \"referencia\": \"$LINK_URL\"}
Añade \"formato\" (Reel/Carrusel/Story/TikTok) SOLO si Gerard lo dice o se ve claro; si no, omítelo."
  fi
  MENSAJE="$MENSAJE

LINK QUE MANDA GERARD (metadatos ya recogidos, NO hace falta que lo abras):
$LINK_INFO

TAREA: es una referencia para una idea de contenido. Resúmela en una frase y guárdala como idea
pendiente ESCRIBIENDO un archivo JSON nuevo en infra/ideas/cola/ (no ejecutes comandos), con:
$LINEA_FORMATO
Añade \"cliente\" (golossa/midtown/jesus-mora/msm/newmos/xavi-colomina) solo si encaja claramente.
Yo lo subo a Notion solo. Luego confírmale a Gerard en corto qué guardaste."
fi

# Lee la respuesta de un JSON de `claude --output-format json`.
# Imprime el texto en stdout, el uso en stderr (al log), y sale != 0 si hubo error.
parse_reply() {
  python3 - "$1" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    sys.stderr.write("  [uso] no pude leer la respuesta (%s)\n" % e)
    sys.exit(1)
u = d.get("usage") or {}
# El total real hay que sumarlo: con caché de prompt, `input_tokens` solo cuenta lo que NO
# venía de la caché, así que por sí solo engaña (sale un "in=9" con 4.000 tokens detrás).
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
    sys.stderr.write("  [error] respuesta vacía\n")
    sys.exit(1)
sys.stdout.write(r)
PY
}

TMP_JSON="$RESP/tmp-reply-$$.json"
trap 'rm -f "$TMP_JSON"' EXIT

# =====================================================================================
# CARRIL 1 — charla (por defecto). Haiku, SIN herramientas, 1 turno, system prompt propio.
# Sin `--tools ""` el arranque cuesta ~24k tokens (system prompt de Claude Code + defs de
# herramientas); con él, ~200. Si hace falta ejecutar algo, Winy responde __ESCALAR__.
# Si venía un link (LINK_URL), se salta el carril 1: ya sabemos que es una tarea (guardar idea).
# =====================================================================================
ok=1
reply=""
if [ -z "$LINK_URL" ]; then
  echo "  -> carril 1 (haiku)" >> "$LOG"
  printf '%s' "$MENSAJE" | claude -p \
    --model claude-haiku-4-5-20251001 \
    --tools "" \
    --disable-slash-commands \
    --no-session-persistence \
    --system-prompt "$(cat "$RESP/winy-system.md")" \
    --max-budget-usd 0.05 \
    --output-format json > "$TMP_JSON" 2>>"$LOG"
  reply=$(parse_reply "$TMP_JSON" 2>>"$LOG"); ok=$?
fi

# =====================================================================================
# CARRIL 2 — tareas. Si el carril 1 pidió escalar, o si venía un link. Sonnet con herramientas.
# =====================================================================================
# ¿El carril 1 ha pedido escalar? Se comprueba sin signos: el modelo tiende a "maquillar" la
# marca (negrita, comillas, guiones), así que comparamos solo las letras.
es_escalada() {
  local s
  s=$(printf '%s' "$1" | tr -d '[:space:][:punct:]' | tr '[:lower:]' '[:upper:]')
  [ "$s" = "ESCALAR" ]
}

if [ -n "$LINK_URL" ] || { [ "$ok" = "0" ] && es_escalada "$reply"; }; then
  echo "  -> carril 2 (sonnet, escalado)" >> "$LOG"
  printf '%s' "$MENSAJE" | claude -p \
    --model claude-sonnet-5 \
    --tools "Bash,Read,Write,Edit,Glob" \
    --disable-slash-commands \
    --no-session-persistence \
    --permission-mode acceptEdits \
    --add-dir "$VAULT" \
    --append-system-prompt "$(cat "$RESP/winy-tareas.md")" \
    --max-budget-usd 0.50 \
    --output-format json > "$TMP_JSON" 2>>"$LOG"
  reply=$(parse_reply "$TMP_JSON" 2>>"$LOG"); ok=$?
fi

# --- Vaciar la bandeja de salida de ideas -------------------------------------------
# En modo headless Winy NO puede ejecutar comandos, así que deja las ideas a guardar como
# `.json` en infra/ideas/cola/. Aquí (bash normal, sin gate de permisos) las subimos a Notion.
COLA="$HUB/infra/ideas/cola"
ideas_ok=0
if ls "$COLA"/*.json >/dev/null 2>&1; then
  ideas_fallo=0
  for f in "$COLA"/*.json; do
    [ -e "$f" ] || continue
    if url=$(python3 "$HUB/infra/notion/idea_add.py" --from-json "$f" 2>>"$LOG"); then
      echo "  -> idea guardada en Notion: $url" >> "$LOG"
      ideas_ok=1
      rm -f "$f"
    else
      ideas_fallo=1
      echo "  -> FALLO guardando idea desde $f (se queda en cola para reintentar)" >> "$LOG"
    fi
  done
  if [ "$ideas_fallo" = "1" ] && [ "$ok" = "0" ]; then
    reply="$reply

⚠️ (No pude guardarla en Notion ahora mismo; la tengo apuntada y lo reintento.)"
  fi
fi

# Los modelos escriben Markdown por costumbre (`**negrita**`), y WhatsApp quiere UN asterisco.
if [ "$ok" = "0" ] && [ -n "$reply" ]; then
  reply=$(printf '%s' "$reply" | python3 "$HUB/infra/formato_wa.py" 2>>"$LOG" || printf '%s' "$reply")
fi

if [ "$ok" != "0" ] || [ -z "$reply" ]; then
  # Fallo (tope de gasto, límite de sesión, API caída…): avisamos, pero NO lo guardamos
  # en memoria — si no, el error se convertiría en "lo último que dijo Winy".
  # Ojo: el fallo puede llegar DESPUÉS de haber hecho el trabajo (típico al saltar el tope de
  # gasto al final). Si la idea sí acabó en Notion, hay que decir la verdad y no "no pude".
  if [ "$ideas_ok" = "1" ]; then
    reply="Guardado ✅ Me quedé sin fuelle para contarte de qué iba, pero la idea ya está en Notion."
  else
    reply="Ey, se me ha cruzado un cable y no he podido contestarte 😅 Dame un minuto y me lo repites."
  fi
  wa_reply "$reply"
  { echo "OUT(fallo, no guardado): $reply"; } >> "$LOG"
  exit 0
fi

wa_reply "$reply"
guardar_memoria "$reply"

{ echo "OUT: $reply"; } >> "$LOG"
