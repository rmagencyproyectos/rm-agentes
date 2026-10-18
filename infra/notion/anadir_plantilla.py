#!/usr/bin/env python3
"""Añade la propiedad `Plantilla` (select) a la Bandeja y a las bases de cliente. Migración idempotente.

Por qué existe: hasta el 13/08/2026 solo se guardaba el `Tipo` (Viral/Marca), que dice el
OBJETIVO de la pieza pero no su MECÁNICA. Sin registrar la mecánica no se puede comparar nada:
el termómetro medía piezas sueltas y no podía responder "¿qué formato funciona con este
cliente?". Esta propiedad es lo que convierte las plantillas de `agentes/guiones/plantillas/`
en algo medible.

Se puede correr las veces que haga falta: Notion fusiona las propiedades, no las reemplaza, y
las opciones que ya existan se quedan como están.

Uso:  anadir_plantilla.py [--dry-run]
Salida: 0 ok · 2 falta token · 1 error
"""
import os
import sys

import notion_api as na

PLANTILLAS_DIR = os.path.join(na.HUB, "agentes/guiones/plantillas")
# Color por plantilla, solo para que el tablero se lea de un vistazo.
COLORES = {
    "humor-situacion": "yellow", "comparativa-duelo": "orange", "demostracion": "blue",
    "pov-trabajador": "purple", "criterio-detalle": "green", "proceso-sin-voz": "pink",
    "pregunta-real": "brown", "historia-a-camara": "red",
}


def plantillas_disponibles():
    """Los nombres de plantilla salen de los .md, para que no haya dos listas que mantener."""
    try:
        return sorted(f[:-3] for f in os.listdir(PLANTILLAS_DIR)
                      if f.endswith(".md") and not f.startswith(("_", "README")))
    except OSError:
        return []


def main():
    dry = "--dry-run" in sys.argv
    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()

    nombres = plantillas_disponibles()
    if not nombres:
        sys.stderr.write(f"No encontré plantillas en {PLANTILLAS_DIR}\n")
        return 1
    print(f"Plantillas encontradas ({len(nombres)}): {', '.join(nombres)}\n")

    opciones = [{"name": n, "color": COLORES.get(n, "default")} for n in nombres]
    payload = {"properties": {
        "Plantilla": {"select": {"options": opciones}},
        # La metodología es la CAPA DE REDACCIÓN (cómo se escribe), distinta de la plantilla
        # (qué tipo de pieza es). Se guarda aparte porque también se está probando.
        "Metodologia": {"select": {"options": [
            {"name": "valor-directo", "color": "blue"},
            {"name": "bucle-abierto", "color": "purple"},
        ]}},
    }}

    fallos = 0
    # La Bandeja también (22/09/2026): Oli propone cada pieza CON su plantilla, y distribuir.py
    # la baja al cliente para que Coco no la vuelva a elegir por su cuenta.
    destinos = [("Bandeja", cfg["bandeja"]["database_id"])]
    destinos += [(cli["label"], cli["database_id"]) for cli in cfg["clientes"].values()]
    for label, db in destinos:
        if dry:
            print(f"(dry-run) añadiría Plantilla a {label}")
            continue
        try:
            na._request("PATCH", f"/databases/{db}", tok, payload)
            print(f"✓ {label}")
        except RuntimeError as e:
            sys.stderr.write(f"✗ {label}: {e}\n")
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
