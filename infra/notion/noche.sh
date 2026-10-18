#!/usr/bin/env bash
# Tanda nocturna de Notion — la dispara launchd a las 00:45 (detrás del check-in de las 00:30).
# Todo lo automático corre de madrugada, nunca de día.
#
#   1. distribuir.py     — baja las ideas Aprobadas de la Bandeja a la base de su cliente
#   2. guionizar.py      — Coco escribe el guion de las marcadas "Coco a guionizar"
#   3. fetch_metricool   — refresca el índice de publicaciones (_posts) con el que se mide todo
#      clasificacion.py  — puente Coco→Analista: etiquetas de cada pieza publicada + snapshot
#                          para el termómetro (qué estructura / tipo de idea / plantilla funciona)
#      panel_datos.py    — panel "Qué vídeos hacer": qué funciona en la agencia (memoria/analisis/)
#   4. autoprogramar.py  — deja BORRADOR en Metricool + copy de Coco de las piezas "Editado"
#                          sin fecha con vídeo final, rellena Notion y avisa (Gate 3: solo borrador)
#
# IMPORTANTE: esto lo lanza launchd (bash normal, sin gate de permisos). NUNCA el responder
# headless: `claude -p --permission-mode acceptEdits` no puede ejecutar Bash. Mismo patrón que
# infra/responder/process.sh con la cola de ideas.
#
#   noche.sh            -> distribuye y guioniza
#   noche.sh --dry-run  -> enseña qué haría, sin tocar nada
# Requisitos: NOTION_API_TOKEN en infra/.env · CLAUDE_CODE_OAUTH_TOKEN en infra/.env.winston.
set -uo pipefail

export PATH="$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
DIR="$HUB/infra/notion"
LOG="$DIR/noche.log"
PY="/usr/bin/python3"   # el único con SSL en este Mac
DRY=""
[ "${1:-}" = "--dry-run" ] && DRY="--dry-run"

cd "$DIR" || exit 1

# Token de larga duración para que guionizar.py pueda llamar a `claude` desatendido (gitignored).
[ -f "$HUB/infra/.env.winston" ] && { set -a; . "$HUB/infra/.env.winston"; set +a; }

{ echo ""; echo "===== $(date '+%Y-%m-%d %H:%M') · tanda notion ====="; } >> "$LOG"

# Cuenta lo que sigue atascado en la Bandeja y lo cachea para el check-in. Va PRIMERO: si el
# gate humano no se aprieta, no hay nada que distribuir y hay que decirlo.
echo "--- bandeja ---" >> "$LOG"
"$PY" "$DIR/bandeja.py" >> "$LOG" 2>&1
echo "  bandeja exit=$?" >> "$LOG"

echo "--- distribuir ---" >> "$LOG"
"$PY" "$DIR/distribuir.py" $DRY >> "$LOG" 2>&1
echo "  distribuir exit=$?" >> "$LOG"

echo "--- guionizar ---" >> "$LOG"
# --avisar: al terminar manda a Gerard un WhatsApp con las ideas guionadas + enlace a Notion.
"$PY" "$DIR/guionizar.py" --avisar $DRY >> "$LOG" 2>&1
echo "  guionizar exit=$?" >> "$LOG"

# Puente Coco → Analista: con qué plantilla y metodología se hizo cada pieza publicada.
# Sin esto el Analista solo puede decir qué vídeo funcionó, no QUÉ funciona. Va después de
# guionizar para recoger lo que se acabe de escribir.
# El cierre del ciclo de aprendizaje: sin métricas frescas no se puede medir nada. Hasta el
# 22/09/2026 esto no lo corría nadie y el índice llevaba parado desde el 11/08 (0 piezas
# medidas). Solo LEE de Metricool; no programa nada. Si falla, se mide con lo que haya.
if [ -z "$DRY" ]; then
  echo "--- metricool ---" >> "$LOG"
  "$PY" "$HUB/infra/metricool/fetch_metricool.py" >> "$LOG" 2>&1
  echo "  metricool exit=$?" >> "$LOG"
fi

echo "--- clasificacion ---" >> "$LOG"
"$PY" "$DIR/clasificacion.py" >> "$LOG" 2>&1
echo "  clasificacion exit=$?" >> "$LOG"

# Bases "📊 Rendimiento de vídeos" (02/10/2026): métricas frescas + vídeos nuevos como filas.
# Solo métricas: nunca toca etiquetas. Xavi va aparte (rendimiento-xavi/semanal.sh, más rico).
if [ -z "$DRY" ]; then
  echo "--- rendimiento ---" >> "$LOG"
  for c in $("$PY" -c "import json;d=json.load(open('$HUB/config/notion-bases.json'))['clientes'];print(' '.join(s+'='+v['rendimiento_db'] for s,v in d.items() if v.get('rendimiento_db') and s!='xavi-colomina'))"); do
    "$PY" "$DIR/rendimiento.py" --cliente "${c%%=*}" --db "${c#*=}" --actualizar >> "$LOG" 2>&1
    echo "  rendimiento ${c%%=*} exit=$?" >> "$LOG"
  done
fi

# Gemini VE los vídeos nuevos y los etiqueta (Gerard, 08/10/2026: "corre Gemini automático").
# Tope de 10 por cliente y noche (~1 céntimo cada uno). Sin Instagram: usa la sesión de Chrome de
# Gerard y de madrugada no se toca; si no hay vídeo en TikTok/Drive/disco, etiqueta desde el copy.
# Va DESPUÉS de rendimiento (que es quien mete las filas nuevas) y ANTES del panel.
if [ -z "$DRY" ]; then
  echo "--- gemini ---" >> "$LOG"
  for c in $("$PY" -c "import json;d=json.load(open('$HUB/config/notion-bases.json'))['clientes'];print(' '.join(s for s,v in d.items() if v.get('rendimiento_db')))"); do
    "$PY" "$HUB/infra/analisis/ver_video.py" --cliente "$c" --max 10 --sin-ig >> "$LOG" 2>&1
    echo "  gemini $c exit=$?" >> "$LOG"
  done
fi

# Creadores de referencia (08/10/2026): de quién son los vídeos de referencia y qué les funciona.
# Solo TikTok automático (metadatos; Gemini ve 1 vídeo por creador nuevo). Instagram: el @ lo pone
# Gerard y el check-in se lo recuerda. Oli lo lee en memoria/analisis/creadores/<cliente>.md.
if [ -z "$DRY" ]; then
  echo "--- referencias ---" >> "$LOG"
  "$PY" "$HUB/infra/olivia/referencias.py" >> "$LOG" 2>&1
  echo "  referencias exit=$?" >> "$LOG"
fi

# Panel "Qué vídeos hacer" (02/10/2026): recalcula qué funciona con las métricas recién bajadas.
# Python puro, 0 tokens. Solo reconstruye memoria/analisis/ + infra/analisis/panel.html; la web
# (Artifact) se republica aparte, cada semana o a demanda.
echo "--- panel ---" >> "$LOG"
"$PY" "$HUB/infra/analisis/panel_datos.py" $DRY >> "$LOG" 2>&1
echo "  panel exit=$?" >> "$LOG"

echo "--- autoprogramar ---" >> "$LOG"
# Deja borradores en Metricool (+copy de Coco) de lo editado sin fecha y avisa por WhatsApp+email.
"$PY" "$HUB/infra/programacion/autoprogramar.py" $DRY >> "$LOG" 2>&1
echo "  autoprogramar exit=$?" >> "$LOG"

echo "fin $(date '+%H:%M')" >> "$LOG"
