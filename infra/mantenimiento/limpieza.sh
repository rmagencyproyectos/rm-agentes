#!/usr/bin/env bash
# Limpieza mensual del sistema (Nova automatizado). Vacía logs volátiles, poda la memoria de
# conversación a 30 días y borra basura (.DS_Store, temporales de audio). NO toca fichas,
# aprendizajes, config, SOPs ni secretos. Lo dispara launchd el día 1 de cada mes (madrugada).
set -uo pipefail
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"

HUB="/Users/gerardruizmiro/rmagency/AGENTES RM"
R="$HUB/infra/responder"
CAMBIOS="$HUB/memoria/cambios-sistema.md"
ts=$(date '+%Y-%m-%d %H:%M')

# 1) Vaciar logs volátiles (en sitio; el servidor/launchd los tienen abiertos)
for f in "$R/responder.log" "$R/server.err.log" "$R/server.out.log" \
         "$HUB/infra/winston/last-run.log" "$HUB/infra/winston/launchd.out.log" \
         "$HUB/infra/winston/launchd.err.log"; do
  [ -f "$f" ] && : > "$f"
done

# 2) Vaciar ids anti-bucle (la protección real es la marca invisible + ventana de 180s)
: > "$R/sent-ids.log" 2>/dev/null || true
: > "$R/seen-ids.log" 2>/dev/null || true

# 3) Podar la memoria de conversación a 30 días (NO la vacía; solo quita lo más viejo)
[ -f "$R/memoria.py" ] && /usr/bin/python3 "$R/memoria.py" render >/dev/null 2>&1 || true

# 4) Borrar basura: .DS_Store y temporales de audio sueltos
dscount=$(find "$HUB" -name .DS_Store 2>/dev/null | wc -l | tr -d ' ')
find "$HUB" -name .DS_Store -delete 2>/dev/null || true
find "$R" -name 'tmp-audio-*' -delete 2>/dev/null || true

# 5) Dejar constancia en el registro de cambios del sistema
{
  printf '\n### %s · Limpieza mensual automática (Nova)\n' "$ts"
  printf -- '- **Pedido por Gerard:** limpieza periódica mensual de registros viejos/inútiles.\n'
  printf -- '- **Cambiado:** vaciados logs volátiles (responder, servidor, check-in) + ids anti-bucle; memoria de conversación podada a 30 días; borrados %s .DS_Store y temporales de audio.\n' "$dscount"
  printf -- '- **Cómo revertir:** no aplica (solo se elimina ruido; nada de datos de negocio se toca).\n'
} >> "$CAMBIOS"
