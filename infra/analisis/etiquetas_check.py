#!/usr/bin/env python3
"""¿Qué opciones de etiqueta hay en Notion que NO están en el vocabulario común? (solo lectura)

Compara el esquema de cada base (Bandeja, Contenido de cada cliente, Rendimiento) con las
listas cerradas de `agentes/guiones/ETIQUETAS.md` y, para cada opción que sobra, cuenta cuántas
filas la usan. Es la entrada para escribir la tabla de `migracion` — y, después de migrar,
la prueba de que no queda nada fuera (debe salir vacío).

Uso:  etiquetas_check.py [--sin-filas]     (--sin-filas: solo esquema, más rápido)
Salida: 0 todo dentro · 3 hay opciones fuera · 2 falta token
"""
import collections
import json
import os
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
import notion_api as na  # noqa: E402

CAMPOS = ("Tipo de idea", "Formato", "Plantilla", "Palanca", "Soporte")


def vocabulario():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import etiquetas as E
    return {k: set(v) for k, v in E.listas().items()}, E.config()


def bases(cfg_notion, cfg_etq):
    out = {"Bandeja": cfg_notion["bandeja"]["database_id"]}
    for slug, c in cfg_notion["clientes"].items():
        out[f"Contenido {slug}"] = c["database_id"]
        if c.get("rendimiento_db"):
            out[f"Rendimiento {slug}"] = c["rendimiento_db"]
    for slug, c in cfg_notion.get("exclientes", {}).items():
        if c.get("rendimiento_db"):
            out[f"Rendimiento {slug}"] = c["rendimiento_db"]
    return out


def main():
    sin_filas = "--sin-filas" in sys.argv
    try:
        tok = na.token()
    except RuntimeError as e:
        print(e)
        return 2
    listas, cfg = vocabulario()
    fuera_total = 0
    for nombre, db in bases(na.load_config(), cfg).items():
        props = na._request("GET", f"/databases/{db}", tok)["properties"]
        uso = collections.defaultdict(collections.Counter)
        if not sin_filas:
            for pg in na.query(db, tok):
                for campo in CAMPOS:
                    v = na.plain(pg["properties"].get(campo))
                    for x in (v if isinstance(v, list) else [v] if v else []):
                        uso[campo][x] += 1
        print(f"\n=== {nombre}")
        for campo in CAMPOS:
            p = props.get(campo)
            if not p:
                print(f"  {campo}: (no existe la columna)")
                continue
            opciones = [o["name"] for o in (p.get(p["type"]) or {}).get("options", [])]
            fuera = [o for o in opciones if o not in listas[campo]]
            faltan = sorted(listas[campo] - set(opciones))
            fuera_total += len(fuera)
            linea = f"  {campo} ({p['type']}): {len(opciones)} opciones"
            if fuera:
                linea += " · FUERA: " + ", ".join(f"{o} [{uso[campo][o]} filas]" for o in fuera)
            if faltan:
                linea += " · faltan: " + ", ".join(faltan)
            print(linea if (fuera or faltan) else linea + " ✓")
    print(f"\n{fuera_total} opciones fuera del vocabulario.")
    return 3 if fuera_total else 0


if __name__ == "__main__":
    sys.exit(main())
