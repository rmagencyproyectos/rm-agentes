#!/usr/bin/env python3
"""Cuenta lo que hay atascado en la Bandeja de Ideas y lo deja en caché.

Por qué existe: la fábrica de Notion tiene **un solo gate humano** — aprobar la idea en la
Bandeja (Estado=Aprobada + Cliente). Si nadie lo aprieta, `distribuir.py` dice "Nada que
distribuir", sale con 0, y todo parece correcto mientras las ideas se pudren. El 11/08/2026
había 14 ideas paradas desde el 26/07 y nada lo decía en ningún sitio.

Esto no arregla la fábrica: la hace **visible**. Escribe una caché que lee `estado.py`, así
el check-in diario lo canta sin que estado.py tenga que salir a la red.

Uso:  bandeja.py            -> imprime y guarda la caché
      bandeja.py --stdout   -> solo imprime (no toca la caché)
"""
import datetime
import os
import sys

import notion_api as na

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
CACHE = os.path.join(HUB, "infra/notion/_bandeja.txt")
# A partir de aquí una idea lleva demasiado parada y se dice en voz alta.
DIAS_RANCIA = 7


def _sel(fila, prop):
    p = fila.get("properties", {}).get(prop, {})
    return (p.get("select") or {}).get("name") if p.get("type") == "select" else None


def resumen():
    tok = na.token()
    cfg = na.load_config()
    filas = na.query(cfg["bandeja"]["database_id"], tok)
    hoy = datetime.date.today()
    con_cliente, sin_cliente, viejas = 0, 0, 0
    for f in filas:
        if _sel(f, "Estado") != "Nueva":
            continue
        if _sel(f, "Cliente"):
            con_cliente += 1
        else:
            sin_cliente += 1
        creada = (f.get("created_time") or "")[:10]
        try:
            if (hoy - datetime.date.fromisoformat(creada)).days >= DIAS_RANCIA:
                viejas += 1
        except ValueError:
            pass
    total = con_cliente + sin_cliente
    if not total:
        return []
    out = [f"- {total} ideas sin triar en la Bandeja"
           + (f" ({viejas} llevan más de {DIAS_RANCIA} días)" if viejas else "")]
    if con_cliente:
        out.append(f"- {con_cliente} ya tienen cliente: solo les falta Estado=Aprobada y "
                   f"esa misma noche salen guionizadas")
    return out


def main():
    try:
        lineas = resumen()
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"No pude leer la Bandeja: {e}\n")
        return 1
    texto = "\n".join(lineas)
    print(texto or "Bandeja al día.")
    if "--stdout" not in sys.argv:
        with open(CACHE, "w", encoding="utf-8") as f:
            f.write(f"# {datetime.datetime.now():%Y-%m-%d %H:%M}\n{texto}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
