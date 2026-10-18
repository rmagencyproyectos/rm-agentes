#!/usr/bin/env bash
# Notificador de RM Agency — cascada WhatsApp → email → push → INBOX.
# Uso:  notify.sh "<mensaje>" [tipo] [urgencia] [canales] [asunto]
#   tipo:     DIGEST_CICLO | CIERRE_MES | LOTE_LISTO | PROBLEMA | CANAL_WA_CAIDO (informativo)
#   urgencia: alta | normal (informativo)
#   canales:  cascada (defecto: el primero que funcione) | wa+email (los DOS, no en cascada;
#             para avisos que Gerard tiene que ver sí o sí, como las propuestas de Oli)
#   asunto:   asunto del correo (opcional; si no, "[RM · <tipo>] aviso (<urgencia>)")
# Siempre anexa al INBOX. Devuelve 0 si algún canal (además del INBOX) tuvo éxito.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HERE/../.env"
INBOX="$HERE/../../INBOX-GERARD.md"
API="http://127.0.0.1:8080"

MSG="${1:?Falta el mensaje}"
TIPO="${2:-AVISO}"
URGENCIA="${3:-normal}"
CANALES="${4:-cascada}"
ASUNTO="${5:-[RM · $TIPO] aviso ($URGENCIA)}"

# Cargar entorno (.env)
set -a; # shellcheck disable=SC1090
. "$ENV_FILE"; set +a

ts() { date '+%Y-%m-%d %H:%M'; }
log() { printf '[%s] %s\n' "$(ts)" "$1" >&2; }

# --- Canal 1: WhatsApp vía Evolution API ---
wa_send() {
  local state
  state=$(curl -s --max-time 8 -H "apikey: $AUTHENTICATION_API_KEY" \
    "$API/instance/connectionState/$WA_INSTANCE" 2>/dev/null \
    | python3 -c "import sys,json;print((json.load(sys.stdin).get('instance') or {}).get('state',''))" 2>/dev/null || echo "")
  if [ "$state" != "open" ]; then
    log "WhatsApp NO disponible (state='$state')"; return 1
  fi
  local resp id payload out
  # Marca invisible (zero-width space): identifica mensajes de la propia Winy para que el
  # responder conversacional no los procese como si fueran mensajes de Gerard (anti-bucle).
  out="${MSG}"$'\xe2\x80\x8b'
  payload=$(NUM="$WA_DESTINO" TXT="$out" python3 -c 'import json,os;print(json.dumps({"number":os.environ["NUM"],"text":os.environ["TXT"]}))')
  resp=$(curl -s --max-time 12 -X POST -H "apikey: $AUTHENTICATION_API_KEY" \
    -H "Content-Type: application/json" "$API/message/sendText/$WA_INSTANCE" \
    -d "$payload" 2>/dev/null || echo "")
  id=$(printf '%s' "$resp" | python3 -c "import sys,json;print((json.load(sys.stdin).get('key') or {}).get('id',''))" 2>/dev/null || echo "")
  # Registrar el id como "enviado por Winy" (segunda barrera anti-bucle del responder)
  if [ -n "$id" ]; then echo "$id" >> "$HERE/../responder/sent-ids.log" 2>/dev/null || true; fi
  if [ -n "$id" ]; then log "WhatsApp OK (id=$id)"; return 0; fi
  log "WhatsApp falló al enviar"; return 1
}

# --- Canal 2: Email (fallback real por SMTP) ---
# Envía por SMTP con /usr/bin/python3 (el único con SSL en este Mac). Se activa SOLO si hay
# SMTP_USER + SMTP_PASS + EMAIL_DESTINO en infra/.env (Gmail: App Password de 16 caracteres,
# NO la contraseña normal). Si faltan, devuelve 1 y la cascada cae al push — headless, 0 tokens.
# (Antes lo mandaba Winston vía Gmail MCP; eso solo funcionaba en sesión interactiva, no en cron.)
email_send() {
  local to="${EMAIL_DESTINO:-}"
  if [ -z "${SMTP_USER:-}" ] || [ -z "${SMTP_PASS:-}" ] || [ -z "$to" ]; then
    log "Email sin configurar (falta SMTP_USER/SMTP_PASS/EMAIL_DESTINO) — salto al siguiente canal"
    return 1
  fi
  if SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}" SMTP_PORT="${SMTP_PORT:-465}" \
     SMTP_USER="$SMTP_USER" SMTP_PASS="$SMTP_PASS" MAIL_TO="$to" \
     MAIL_SUBJECT="$ASUNTO" MAIL_BODY="$MSG" \
     /usr/bin/python3 "$HERE/send_email.py" >>/dev/null 2>&1; then
    log "Email OK → $to"; return 0
  fi
  log "Email falló al enviar"; return 1
}

# --- Canal 3: Push (fallback real) ---
# 1º notificación local de macOS (osascript, 0 credenciales, sirve cuando estás en el Mac).
# 2º opcional: push al móvil vía ntfy.sh si NTFY_TOPIC está en .env (te suscribes al topic en
#    la app ntfy). Ambos best-effort; devuelve 0 si alguno entró.
push_send() {
  if command -v osascript >/dev/null 2>&1; then
    local m t
    m=$(printf '%s' "$MSG" | head -c 400 | tr '\n' ' ' | sed 's/"/\\"/g')
    t=$(printf 'RM · %s' "$TIPO" | sed 's/"/\\"/g')
    if osascript -e "display notification \"$m\" with title \"$t\"" >/dev/null 2>&1; then
      log "Push (notificación macOS) OK"; return 0
    fi
  fi
  if [ -n "${NTFY_TOPIC:-}" ]; then
    if curl -s --max-time 8 -H "Title: RM · $TIPO" -d "$MSG" \
       "https://ntfy.sh/${NTFY_TOPIC}" >/dev/null 2>&1; then
      log "Push (ntfy) OK"; return 0
    fi
  fi
  log "Push no disponible (ni osascript ni NTFY_TOPIC)"; return 1
}

# --- Canal 4: INBOX (siempre) ---
inbox_write() {
  local mark="$1"
  { printf '\n### %s · %s · %s %s\n%s\n' "$(ts)" "$TIPO" "$URGENCIA" "$mark" "$MSG"; } >> "$INBOX"
}

delivered=""
if [ "$CANALES" = "wa+email" ]; then
  # Los dos, independientes: que falle uno no impide el otro.
  wa_send && delivered="whatsapp"
  if email_send; then delivered="${delivered:+$delivered+}email"; fi
  [ -z "$delivered" ] && push_send && delivered="push"
elif wa_send; then delivered="whatsapp";
elif email_send; then delivered="email";
elif push_send; then delivered="push";
fi

if [ -n "$delivered" ]; then
  inbox_write "(enviado por: $delivered)"
  log "Notificado por $delivered + INBOX"; exit 0
else
  inbox_write "(⚠️ solo INBOX — todos los canales fallaron)"
  log "Ningún canal disponible; solo INBOX"; exit 1
fi
