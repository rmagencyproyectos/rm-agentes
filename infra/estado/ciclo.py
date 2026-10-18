#!/usr/bin/env python3
"""El reloj: qué fase del ciclo le toca a cada cliente esta semana.

Cada cliente pasa por las mismas 4 fases cada mes (analizar → guiones → grabar → editar),
pero **desfasado** respecto a los demás. Así cada semana hay siempre una grabación, una
edición, un análisis y unos guiones — en vez de tres semanas muertas y una avalancha.

Datos en `config/ciclo-mensual.json` (fuente única). Python puro, 0 tokens.

Uso:
  ciclo.py              -> qué toca esta semana
  ciclo.py --mes        -> la tabla del mes entero
  ciclo.py --fecha YYYY-MM-DD  -> como si hoy fuera esa fecha
"""
import datetime
import json
import os
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
CONFIG = os.path.join(HUB, "config/ciclo-mensual.json")
NOMBRES = {"jesus-mora": "Jesús Mora", "xavi-colomina": "Xavi", "golossa": "Golossa",
           "midtown": "Midtown", "msm": "MSM", "newmos": "Newmos"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def cargar():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def semana_de(fecha):
    """Semana del ciclo (1-4). S1=días 1-7, S2=8-14, S3=15-21, S4=22 a fin de mes.

    Los meses de 29-31 días alargan la S4; es a propósito: mejor una semana larga que una
    quinta semana suelta que descuadre el desfase de todos los clientes.
    """
    return min(4, (fecha.day - 1) // 7 + 1)


def fase_de(cliente, fecha, cfg=None):
    """Fase que le toca al cliente en esa fecha, o None si está fuera del reloj."""
    cfg = cfg or cargar()
    desfase = cfg["desfase"].get(cliente)
    if desfase is None:
        return None
    fases = cfg["fases"]
    return fases[(semana_de(fecha) - 1 + desfase) % len(fases)]


def informe(fecha=None, cfg=None):
    """Líneas compactas de qué le toca a cada cliente esta semana."""
    fecha = fecha or datetime.date.today()
    cfg = cfg or cargar()
    sem = semana_de(fecha)
    lineas = [f"Semana {sem} del ciclo ({MESES[fecha.month - 1]} {fecha.year}):"]
    # Ordenado por fase, para que se lea como un plan y no como una lista de clientes.
    orden = {f["id"]: i for i, f in enumerate(cfg["fases"])}
    filas = []
    for cli in cfg["desfase"]:
        f = fase_de(cli, fecha, cfg)
        filas.append((orden[f["id"]], f, cli))
    for _, f, cli in sorted(filas):
        lineas.append(f"  {f['emoji']} {NOMBRES.get(cli, cli)} — {f['nombre'].lower()}: {f['que']}")
    return lineas


def tabla_mes(fecha=None, cfg=None):
    """La rejilla del mes entero: filas = clientes, columnas = semanas."""
    fecha = fecha or datetime.date.today()
    cfg = cfg or cargar()
    clientes = list(cfg["desfase"])
    ancho = max(len(NOMBRES.get(c, c)) for c in clientes)
    # Los emojis ocupan dos columnas en terminal, así que se separa con "|" en vez de padear.
    out = [f"{MESES[fecha.month - 1]} {fecha.year}", "",
           " " * ancho + " | " + " | ".join(f"S{s}         " for s in range(1, 5))]
    for cli in clientes:
        celdas = [f"{fase_de(cli, fecha.replace(day=1 + (s - 1) * 7), cfg)['emoji']} "
                  f"{fase_de(cli, fecha.replace(day=1 + (s - 1) * 7), cfg)['corto']:<9}"
                  for s in range(1, 5)]
        out.append(f"{NOMBRES.get(cli, cli):<{ancho}} | " + " | ".join(celdas))
    return out


def main():
    fecha = None
    if "--fecha" in sys.argv:
        try:
            fecha = datetime.date.fromisoformat(sys.argv[sys.argv.index("--fecha") + 1])
        except (IndexError, ValueError):
            print("uso: ciclo.py [--mes] [--fecha YYYY-MM-DD]")
            return 2
    lineas = tabla_mes(fecha) if "--mes" in sys.argv else informe(fecha)
    print("\n".join(lineas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
