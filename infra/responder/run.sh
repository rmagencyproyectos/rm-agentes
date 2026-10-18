#!/usr/bin/env bash
# Arranca el servidor webhook de Winy conversacional. Lo mantiene vivo launchd (KeepAlive).
set -uo pipefail
export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
set -a; . "$HUB/infra/.env"; set +a
exec /usr/bin/python3 "$HUB/infra/responder/webhook.py"
