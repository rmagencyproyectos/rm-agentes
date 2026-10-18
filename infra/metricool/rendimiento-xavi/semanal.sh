#!/bin/bash
# Refresco semanal de la base «📊 Rendimiento de vídeos (Metricool)» de Xavi.
# Lo lanza launchd (com.rmagency.xavi-rendimiento) los sábados a las 06:00; si el Mac estaba
# dormido, lo corre al despertar. Vive en el hub y no en el disco externo porque macOS no deja
# a launchd leer volúmenes externos sin dar «Acceso total al disco» (25/09/2026).
AQUI="$(cd "$(dirname "$0")" && pwd)"
LOG="$HOME/Library/Logs/xavi-rendimiento.log"
echo "=== $(date '+%Y-%m-%d %H:%M') ===" >> "$LOG"
cd "$AQUI" || exit 1
/usr/bin/python3 metricool_a_notion.py >> "$LOG" 2>&1
/usr/bin/python3 ganchos.py >> "$LOG" 2>&1
