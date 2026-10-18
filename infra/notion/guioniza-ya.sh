#!/usr/bin/env bash
# "Guioniza ya" — disparador de URGENCIA para guionizar sin esperar a la madrugada.
#
# El flujo normal guioniza de noche (barato, en tanda). Esto es la vía rápida para cuando
# necesitas un guion AHORA: reparte lo aprobado y guioniza al momento (~1 min por idea).
#
#   guioniza-ya.sh                 -> reparte + guioniza TODO lo que esté pendiente
#   guioniza-ya.sh golossa         -> solo ese cliente
#   guioniza-ya.sh golossa 1       -> solo ese cliente, tope 1 guion
#
# NO es un botón de Notion (Notion no ejecuta scripts). Es un comando: lo corre Gerard en una
# sesión, o Winy cuando Gerard le dice "guioniza ya la de Golossa" por WhatsApp (vía la cola).
set -uo pipefail

export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
DIR="$HUB/infra/notion"
PY="/usr/bin/python3"
CLIENTE="${1:-}"
MAX="${2:-3}"

[ -f "$HUB/infra/.env.winston" ] && { set -a; . "$HUB/infra/.env.winston"; set +a; }
cd "$DIR" || exit 1

ARGS=()
[ -n "$CLIENTE" ] && ARGS+=(--cliente "$CLIENTE")

echo "== reparto rápido =="
"$PY" "$DIR/distribuir.py" "${ARGS[@]}"
echo "== guion rápido (tope $MAX) =="
"$PY" "$DIR/guionizar.py" "${ARGS[@]}" --max "$MAX"
