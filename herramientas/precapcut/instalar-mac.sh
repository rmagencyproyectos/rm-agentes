#!/bin/bash
# Instala precapcut en un Mac (sin sudo). Uso: bash instalar-mac.sh
set -e
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Falta Node 18+: https://nodejs.org (instalador .pkg)"; exit 1; }
command -v capcut >/dev/null || npm i -g capcut-cli@0.31.1
python3 -m pip install --user -q -r requirements.txt
# descarga el modelo una vez para que la primera pieza no espere
python3 -c "from faster_whisper import WhisperModel; WhisperModel('medium', compute_type='int8')"
# fuentes de las marcas (estilos/), solo para este usuario
mkdir -p ~/Library/Fonts && cp -n fuentes/*.ttf ~/Library/Fonts/ || true
# efectos de sonido (Mixkit): solo descarga los que falten
python3 sonidos/descargar.py
command -v ffprobe >/dev/null || echo "Sin ffprobe: se usará ffprobe_pyav.py (normal en este Mac)."
capcut doctor -H || true
echo
echo "CapCut instalado: $(defaults read /Applications/CapCut.app/Contents/Info.plist CFBundleShortVersionString 2>/dev/null || echo '?')"
echo "IMPORTANTE: probado con CapCut 9.5. NO actualices a la 10 (rechaza estos proyectos)."
