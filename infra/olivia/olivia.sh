#!/usr/bin/env bash
# Lanzador de Olivia (Oli) — abre una sesión INTERACTIVA de Claude Code en el hub, con el
# kickoff de la estratega ya cargado.
#
# Desde el 22/09/2026 la tanda mensual la monta Oli SOLA (infra/olivia/oli_noche.py, miércoles
# 01:30 de la semana 📊 de cada cliente) y Gerard la valida en Notion. Esto queda para cuando
# se quiera trabajar una tanda conversando. Si se hace a mano, al terminar súbela con
# infra/olivia/a_bandeja.py (lo dice el kickoff).
#
# Uso:  olivia.sh golossa                 -> tanda del ciclo actual
#       olivia.sh jesus-mora 2026-09      -> tanda de un ciclo concreto
set -euo pipefail

HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
KICKOFF="$HUB/infra/olivia/kickoff.md"
CLIENTE="${1:-}"
CICLO="${2:-$(date +%Y-%m)}"

if [ -z "$CLIENTE" ]; then
  echo "uso: olivia.sh <cliente> [YYYY-MM]" >&2
  echo "clientes: $(python3 -c "
import json,sys
with open('$HUB/config/notion-bases.json') as f:
    print(', '.join(json.load(f)['clientes']))
" 2>/dev/null || echo 'ver config/notion-bases.json')" >&2
  exit 2
fi
[ -f "$KICKOFF" ] || { echo "No encuentro el kickoff: $KICKOFF" >&2; exit 1; }

if ! grep -q "\"$CLIENTE\"" "$HUB/config/notion-bases.json"; then
  echo "Cliente desconocido: $CLIENTE (mira config/notion-bases.json)" >&2
  exit 2
fi

PROMPT="$(cat "$KICKOFF")

---
Cliente de esta sesión: **$CLIENTE**. Ciclo: **$CICLO**.
El archivo que tienes que dejar escrito es \`ciclos/$CICLO/$CLIENTE/hipotesis.json\`."

cd "$HUB" || exit 1
exec claude "$PROMPT"
