#!/usr/bin/env python3
"""Borra los registros de copy cuya fecha de publicación ya pasó (retención de copies).

Regla de Gerard: el copy de un vídeo se guarda SOLO hasta su fecha de programación; pasada esa
fecha, el registro se borra para no acumular copies. Este script (Python puro, 0 tokens) recorre
todos los registros de copy del sistema y borra los vencidos. Es idempotente y silencioso; lo
lanza launchd de madrugada (nunca de día — ver memoria "horario tareas de madrugada").

Cada registro vive en `ciclos/<ciclo>/<cliente>/copies/*.md` y lleva su fecha en el frontmatter:

    ---
    fecha: 2026-07-29        # fecha de publicación programada (YYYY-MM-DD)
    ...
    ---
    <el copy>

- Si `fecha` < hoy  -> se borra el fichero.
- Si no hay `fecha` (o no parsea) -> NO se toca (seguridad: no borramos registros sin fecha).

Uso:
  limpiar_copies.py            -> borra los vencidos, imprime un resumen
  limpiar_copies.py --dry-run  -> solo dice qué borraría, sin tocar nada
"""
import argparse
import datetime
import glob
import os
import re
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
FECHA_RE = re.compile(r"^fecha:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def fecha_de(ruta):
    """Devuelve la fecha (date) del frontmatter del copy, o None si no la tiene/ no parsea."""
    try:
        with open(ruta, encoding="utf-8") as f:
            cabecera = f.read(2000)  # el frontmatter va al principio; no hace falta leer todo
    except OSError:
        return None
    m = FECHA_RE.search(cabecera)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="No borra; solo dice qué borraría")
    a = ap.parse_args()

    hoy = datetime.date.today()
    patron = os.path.join(HUB, "ciclos", "*", "*", "copies", "*.md")
    borrados, conservados, sin_fecha = 0, 0, 0
    for ruta in glob.glob(patron):
        fecha = fecha_de(ruta)
        if fecha is None:
            sin_fecha += 1
            continue
        if fecha < hoy:
            rel = os.path.relpath(ruta, HUB)
            if a.dry_run:
                print(f"[dry-run] borraría {rel} (fecha {fecha})")
            else:
                try:
                    os.remove(ruta)
                    print(f"borrado {rel} (fecha {fecha})")
                except OSError as e:
                    sys.stderr.write(f"no pude borrar {rel}: {e}\n")
                    continue
            borrados += 1
        else:
            conservados += 1

    print(f"copies: {borrados} vencidos {'(dry-run) ' if a.dry_run else ''}· "
          f"{conservados} vigentes · {sin_fecha} sin fecha (intactos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
