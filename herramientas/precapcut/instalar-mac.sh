#!/bin/bash
# Instala precapcut en un Mac (sin sudo). Uso: bash instalar-mac.sh
set -e
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Falta Node 18+: https://nodejs.org (instalador .pkg)"; exit 1; }
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" || { echo "Falta Python 3.9+: https://python.org"; exit 1; }
command -v capcut >/dev/null || npm i -g capcut-cli@0.31.1
python3 -m pip install --user -q -r requirements.txt
# descarga el modelo una vez para que la primera pieza no espere
python3 -c "from faster_whisper import WhisperModel; WhisperModel('medium', compute_type='int8')"
# fuentes de las marcas (estilos/), solo para este usuario
mkdir -p ~/Library/Fonts && cp -n fuentes/*.ttf ~/Library/Fonts/ || true
# plantillas de gráficos (fase 2b): Remotion. En el Mac de Gerard es un enlace; en los demás se instala.
[ -e recursos/remotion/node_modules ] || (cd recursos/remotion && npm i --no-audit --no-fund --silent)
command -v ffprobe >/dev/null || echo "Sin ffprobe: se usará ffprobe_pyav.py (normal en este Mac)."
capcut doctor -H || true
echo
echo "CapCut instalado: $(defaults read /Applications/CapCut.app/Contents/Info.plist CFBundleShortVersionString 2>/dev/null || echo '?')"
echo "IMPORTANTE: probado con CapCut 9.5. NO actualices a la 10 (rechaza estos proyectos)."
