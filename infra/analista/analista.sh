#!/usr/bin/env bash
# Lanzador del Analista — abre una sesión INTERACTIVA de Claude Code en el repo del
# análisis mensual, con el kickoff cargado.
#
# ⚠️ NO es headless y NO lo dispara launchd: el Analista necesita los conectores de
#    Canva, Gmail y Chrome + acceso a ~/Documents + verificación visual en Canva. Por eso
#    corre en sesión interactiva (la app/CLI donde esos conectores están configurados).
#    El "disparador" automático es solo el AVISO del check-in diario de Winy (ver
#    infra/estado/estado.py → leer_analisis_pendiente); esto es lo que arrancas tú al leerlo.
#
# Uso:  analista.sh              -> arranca el Analista (él mira en el registro qué falta)
#       analista.sh "Golossa"    -> arranca centrado en un cliente
set -euo pipefail

HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
ANALISIS="/Users/gerardruizmiro/rmagency/proyectos/Analisis mensual"
KICKOFF="$HUB/infra/analista/kickoff.md"
CLIENTE="${1:-}"

[ -f "$KICKOFF" ] || { echo "No encuentro el kickoff: $KICKOFF" >&2; exit 1; }
[ -d "$ANALISIS" ] || { echo "No encuentro el repo de análisis: $ANALISIS" >&2; exit 1; }

PROMPT="$(cat "$KICKOFF")"
[ -n "$CLIENTE" ] && PROMPT="$PROMPT"$'\n\n'"Cliente para esta sesión: $CLIENTE."

cd "$ANALISIS" || exit 1
exec claude "$PROMPT"
