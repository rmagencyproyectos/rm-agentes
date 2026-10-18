#!/usr/bin/env bash
# Oli sola (22/09/2026). La lanza launchd:
#   miércoles 01:30  -> oli-noche.sh              tanda de los clientes en su semana 📊 Analizar
#                       (va detrás de notion/noche.sh de las 00:45, que refresca Metricool)
#   sábado 10:00     -> oli-noche.sh --recordatorio   avisa de lo que siga sin revisar
# Bash normal, sin gate de permisos (mismo patrón que notion/noche.sh).
set -uo pipefail
export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
LOG="$HUB/infra/olivia/oli-noche.log"
# Token de larga duración para que `claude -p` funcione desatendido (gitignored).
[ -f "$HUB/infra/.env.winston" ] && { set -a; . "$HUB/infra/.env.winston"; set +a; }
cd "$HUB" || exit 1
{ echo ""; echo "===== $(date '+%Y-%m-%d %H:%M') · oli ${1:-} ====="; } >> "$LOG"
/usr/bin/python3 "$HUB/infra/olivia/oli_noche.py" "$@" >> "$LOG" 2>&1
echo "  exit=$?" >> "$LOG"
