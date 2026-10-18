#!/usr/bin/env bash
# Lanza el chequeo de cobertura y lo envía por WhatsApp (Winy). Lo dispara launchd (lun y jue).
set -uo pipefail
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/node/bin"
/usr/bin/python3 "/Users/gerardruizmiro/rmagency/AGENTES RM/infra/metricool/chequeo_cobertura.py" --send
