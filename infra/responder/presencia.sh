#!/usr/bin/env bash
# Mantiene a Winy como dispositivo "no disponible" ante WhatsApp.
#
# Por qué: Winy es un dispositivo vinculado 24/7. Si WhatsApp lo ve "activo", deja de mandar
# las notificaciones push al MÓVIL de Gerard (asume que ya las está leyendo en el ordenador).
# `alwaysOnline:false` en los settings no basta: cada vez que Baileys reconecta solo —el
# websocket se cae y se levanta sin reiniciar el contenedor— vuelve a registrar presencia y
# las notificaciones desaparecen otra vez, sin ningún aviso.
#
# Por eso esto se reaplica cada 5 min desde launchd (com.rmagency.presencia.plist).
# Silencioso si va bien; solo escribe en el log cuando falla.
set -uo pipefail
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
LOG="$HUB/infra/responder/presencia.log"
set -a; . "$HUB/infra/.env"; set +a

API="${API:-http://127.0.0.1:8080}"
code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' \
  -X POST -H "apikey: $AUTHENTICATION_API_KEY" -H "Content-Type: application/json" \
  "$API/instance/setPresence/$WA_INSTANCE" \
  -d '{"presence":"unavailable"}' 2>/dev/null || echo "000")

# 201 = aplicado. Cualquier otra cosa (Docker parado, sesión caída, API cambiada) se apunta.
if [ "$code" != "201" ] && [ "$code" != "200" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') · fallo setPresence (HTTP $code)" >> "$LOG"
fi
