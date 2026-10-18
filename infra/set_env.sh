#!/usr/bin/env bash
# Pone/actualiza un secreto en infra/.env SIN mostrarlo por pantalla ni dejarlo en el historial.
# Uso:  infra/set_env.sh NOMBRE_CLAVE
#   p.ej.  infra/set_env.sh NOTION_API_TOKEN
#          infra/set_env.sh SMTP_PASS
# Si la clave ya existe (aunque esté comentada con #), la reemplaza. Si no, la añade al final.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HERE/.env"
KEY="${1:?Uso: set_env.sh NOMBRE_CLAVE}"

# Validación básica del nombre de la clave
if ! printf '%s' "$KEY" | grep -qE '^[A-Z0-9_]+$'; then
  echo "Nombre de clave inválido: '$KEY' (solo A-Z 0-9 _)" >&2; exit 1
fi

printf 'Valor para %s (no se mostrará): ' "$KEY" >&2
# Lectura oculta compatible con bash y zsh
stty -echo 2>/dev/null || true
IFS= read -r VALUE
stty echo 2>/dev/null || true
printf '\n' >&2

if [ -z "$VALUE" ]; then echo "Vacío, no toco nada." >&2; exit 1; fi

# Quita TODOS los espacios/tabuladores del valor: los secretos (tokens, App Passwords, topics)
# no llevan espacios, y un espacio dentro del valor rompe el `. .env` de bash (set -e aborta).
VALUE="$(printf '%s' "$VALUE" | tr -d '[:space:]')"

touch "$ENV_FILE"
# backup
cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d-%H%M%S)"

# Reescribe con python (maneja bien líneas comentadas y valores con caracteres raros)
KEY="$KEY" VALUE="$VALUE" ENV_FILE="$ENV_FILE" /usr/bin/python3 - <<'PY'
import os
key=os.environ["KEY"]; val=os.environ["VALUE"]; path=os.environ["ENV_FILE"]
lines=open(path).read().splitlines()
out=[]; hecho=False
for l in lines:
    s=l.strip()
    # coincide con "KEY=" o "#KEY=" o "# KEY="
    core=s[1:].strip() if s.startswith("#") else s
    if core.startswith(key+"="):
        if not hecho:
            out.append(f"{key}={val}"); hecho=True
        # si había duplicados, los descarta
        continue
    out.append(l)
if not hecho:
    if out and out[-1].strip()!="": out.append("")
    out.append(f"{key}={val}")
open(path,"w").write("\n".join(out).rstrip()+"\n")
print(f"{key} actualizado ✅ (longitud {len(val)})")
PY

echo "Backup previo guardado. Listo." >&2
