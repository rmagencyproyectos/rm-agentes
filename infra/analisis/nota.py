#!/usr/bin/env python3
"""La NOTA de un vídeo, igual para todos los clientes. Se importa; no es un CLI.

Misma regla que `infra/notion/rendimiento.py` (Gerard, 29/09/2026): **las vistas solas
engañan**. Cada vídeo se mide en dos ejes contra lo normal DE ESE CLIENTE en cada red:
  - alcance:   vistas / mediana de vistas de la red
  - conexión:  % interacción (interacciones / vistas) / mediana de ese % en la red
NOTA = media geométrica de los dos. 1.0 = un vídeo normal de ese cliente. Geométrica a
propósito: un 0 en un eje no se tapa con el otro.

Por qué vive aparte: Xavi tiene IG + TikTok + YouTube con columnas sueltas (likes,
comentarios…) y Golossa IG + TikTok con interacciones ya sumadas. Esto convierte las dos
formas en `{red: (vistas, interacciones)}` y les pasa la misma fórmula, para que una nota
de Xavi y una de Golossa se puedan poner en el mismo ranking.
"""
import statistics

REDES = ("IG", "TT", "YT")


def _num(props, k):
    p = props.get(k) or {}
    if p.get("type") == "number":
        return p.get("number") or 0
    if p.get("type") == "formula":
        return (p.get("formula") or {}).get("number") or 0
    return 0


def redes_de(props):
    """{red: (vistas, interacciones)} de una fila de cualquier base de rendimiento."""
    out = {}
    for r in REDES:
        vistas = _num(props, f"{r} Vistas")
        if not vistas:
            continue
        inter = _num(props, f"{r} Interacciones")
        if not inter:   # Xavi: TikTok y YouTube vienen desglosados
            inter = sum(_num(props, f"{r} {k}") for k in ("Likes", "Comentarios", "Compartidos", "Guardados"))
        out[r] = (vistas, inter)
    return out


def medianas(filas_redes):
    """Lo normal del cliente: mediana de vistas y de % interacción por red."""
    vistas, eng = {}, {}
    for redes in filas_redes:
        for r, (v, i) in redes.items():
            vistas.setdefault(r, []).append(v)
            eng.setdefault(r, []).append(i / v)
    return ({r: statistics.median(x) for r, x in vistas.items()},
            {r: statistics.median(x) for r, x in eng.items()})


def nota(redes, med_vistas, med_eng):
    """(nota, ratio_vistas, ratio_interaccion). 0 si no hay con qué comparar."""
    if not redes:
        return 0, 0, 0
    vistas = sum(v for v, _ in redes.values())
    esperado = sum(med_vistas.get(r, 0) for r in redes)
    inter = sum(i for _, i in redes.values())
    esperado_eng = statistics.mean([med_eng.get(r, 0) for r in redes])
    if not (esperado and esperado_eng and vistas):
        return 0, 0, 0
    rv = vistas / esperado
    re = (inter / vistas) / esperado_eng
    n = (rv * re) ** 0.5 if (rv and re) else 0
    return round(n, 2), round(rv, 2), round(re, 2)
