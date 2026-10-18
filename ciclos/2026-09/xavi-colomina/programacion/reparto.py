#!/usr/bin/env python3
"""Inventario de Drive por SERIE + reparto uniforme en el calendario de Xavi.

A diferencia de listar_videos.py (que aplana todas las subcarpetas), aquí la subcarpeta
importa: es la serie, y el reparto uniforme se hace entre series.

Salida: ciclos/2026-09/xavi-colomina/programacion/videos.json
"""
import datetime
import json
import os
import re
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/programacion"))
sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
import listar_videos as lv          # noqa: E402  (auth + helpers de Drive)
import chequeo_cobertura as cob     # noqa: E402  (días de publicación: fuente única)

CLIENTE = "xavi-colomina"
INICIO = datetime.date(2026, 9, 1)
HORA = "15:00"

# Series que entran en la rotación, en orden de "peso" para el desempate.
SERIES = ["TIPS ENTRENO", "PODCAST", "EJERCICIOS", "EXPLICACIONES"]

# Fuera de la rotación:
EXCLUIR_CARPETAS = {"PRESENTACIÓ INTRO  XARXES"}   # intro/outro de Jaume, no son piezas
EXCLUIR_ARCHIVOS = {"PODCAST1.mp4"}                # bruto de 2 GB


def inventario(service, raiz):
    """{serie: [ {archivo, titulo, id, url} ... ]} ordenado dentro de cada serie."""
    resp = service.files().list(
        q=f"'{raiz}' in parents and trashed=false and "
          f"mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)", pageSize=100,
        includeItemsFromAllDrives=True, supportsAllDrives=True,
    ).execute()

    out = {}
    for carpeta in resp.get("files", []):
        nombre = carpeta["name"]
        if nombre in EXCLUIR_CARPETAS:
            continue
        vids = lv.listar_recursivo(service, carpeta["id"], profundidad=2)
        vids = [v for v in vids if v["name"] not in EXCLUIR_ARCHIVOS]
        vids.sort(key=lambda v: orden_serie(v["name"]))
        if nombre == "TIPS ENTRENO":
            vids = alternar_tanda(vids)
        out[nombre] = [{
            "archivo": v["name"],
            "titulo": titulo(v["name"]),
            "drive_id": v["id"],
            "url": f"https://drive.google.com/file/d/{v['id']}/view",
        } for v in vids]
    return out


def alternar_tanda(vids):
    """Intercala los tips de título propio con los 'Tanda 3-N'.

    Los 18 'Tanda 3-N' salen de una sola sesión (15/05) y se parecen entre sí: publicados
    seguidos, el feed de noviembre-diciembre se vería clonado. Se reparten uno a uno contra
    los 16 de título propio.
    """
    tanda = [v for v in vids if re.match(r"Tanda\s", v["name"], re.I)]
    propio = [v for v in vids if v not in tanda]
    largo, corto = (tanda, propio) if len(tanda) >= len(propio) else (propio, tanda)
    out = []
    for i, v in enumerate(largo):
        out.append(v)
        if i < len(corto):
            out.append(corto[i])
    return out


def orden_serie(nombre):
    """Dentro de una serie: primero los de título propio, luego los 'Tanda 3-N' por número.

    Los C01/C02... del podcast conservan su orden numérico (es el orden del episodio).
    """
    m = re.match(r"C(\d+)_", nombre)
    if m:
        return (0, int(m.group(1)), "")
    m = re.match(r"Tanda\s+(\d+)-(\d+)", nombre, re.I)
    if m:
        return (2, int(m.group(1)) * 1000 + int(m.group(2)), "")
    m = re.match(r"Ejercicio\s+(\d+)", nombre, re.I)
    if m:
        return (1, int(m.group(1)), "")
    return (1, 0, nombre.lower())


# Los nombres de archivo vienen del editor, sin acentos ni mayúsculas. En Notion los ve el
# cliente, así que se escriben bien. Los "Tanda 3-N" se dejan intactos: su nombre no dice de
# qué van y no hay que inventárselo.
ARREGLOS = {
    "Tanda 3-1": "Defensa: cierra la línea directa",
    "Tanda 3-2": "Juega al contrapié de su cintura",
    "Tanda 3-3": "Un paso atrás para ver el globo",
    "Tanda 3-4": "Baja el centro de gravedad",
    "Como Ganar partidos": "Cómo ganar partidos",
    "Como recibir globo": "Cómo recibir un globo",
    "comodidad vs incomodidad": "Comodidad vs incomodidad",
    "El mejor golpeo": "El mejor golpeo",
    "Evitar angulos": "Evitar ángulos",
    "Fallo de Movimiento-1": "Fallo de movimiento",
    "Importancia de estar alineado": "La importancia de estar alineado",
    "Importancia de los movimientos": "La importancia de los movimientos",
    "Importancia dela 2a bola": "La importancia de la 2ª bola",
    "La mejor bola": "La mejor bola",
    "Posicion ataque cruzado": "Posición de ataque cruzado",
    "Posicion de defensa": "Posición de defensa",
    "Veis el error?": "¿Veis el error?",
    "Veis el error 2": "¿Veis el error? (2)",
    "Asi juega un pro": "Así juega un pro",
    "Entrena tu lado debil": "Entrena tu lado débil",
    "Roba tiempo al rival": "Roba tiempo al rival",
    "C01 — Coaching mierda": "C01 — El coaching de mierda",
    "C02 — Proverbio arabe": "C02 — El proverbio árabe",
    "C04 — Relacion contigo mismo": "C04 — La relación contigo mismo",
    "C07 — Critica ego estrella": "C07 — Crítica, ego y estrella",
    "C09 — Padel es un rio": "C09 — El pádel es un río",
    "C10 — Ojala a los 20": "C10 — Ojalá lo hubiera sabido a los 20",
    "C11 — Problema es un reto": "C11 — El problema es un reto",
    "C12 — No es padel es tu ego": "C12 — No es el pádel, es tu ego",
    "C14 — Bloopers intro": "C14 — Bloopers",
}


def titulo(nombre):
    stem = os.path.splitext(nombre)[0]
    m = re.match(r"C(\d+)_(.+?)_vertical$", stem)
    if m:
        crudo = f"C{m.group(1)} — " + m.group(2).replace("-", " ").capitalize()
    else:
        crudo = re.sub(r"^Xavi Colomina - ", "", stem).replace("_", " ").strip()
    return ARREGLOS.get(crudo, crudo)


def reparto(inv):
    """Interleave uniforme: cada serie se estira sobre [0,1) y se ordena por esa posición.

    Con 34 tips / 9 podcast / 5 ejercicios / 3 explicaciones sobre 51 huecos sale, de media,
    2 piezas de pista + 1 de otra serie por semana. Nada se agrupa.
    """
    marcados = []
    for serie, items in inv.items():
        n = len(items)
        peso = SERIES.index(serie) if serie in SERIES else len(SERIES)
        for i, it in enumerate(items):
            marcados.append(((i + 0.5) / n, peso, i, serie, it))
    marcados.sort(key=lambda t: (t[0], t[1], t[2]))
    return [(serie, it) for _, _, _, serie, it in marcados]


def fechas(n, desde):
    """Los próximos n días de publicación del cliente a partir de `desde` (incluido)."""
    out, d = [], desde
    while len(out) < n:
        if d.weekday() in cob.dias_para(CLIENTE, d):
            out.append(d)
        d += datetime.timedelta(days=1)
    return out


def main():
    service = lv.construir_servicio(lv.load_env())
    if service is None:
        return 2
    raiz = lv.carpeta_cliente(CLIENTE)
    inv = inventario(service, raiz)

    print("Inventario por serie:")
    for s in SERIES:
        print(f"  {s:16} {len(inv.get(s, [])):>3}")
    total = sum(len(v) for v in inv.values())
    print(f"  {'TOTAL':16} {total:>3}  (+1 presentación = {total + 1} posts)\n")

    orden = reparto(inv)
    dias = fechas(total + 1, INICIO)

    posts = [{
        "n": 1,
        "fecha": dias[0].isoformat(),
        "hora": HORA,
        "serie": "PRESENTACIÓN",
        "titulo": "Presentació Xavi Colomina",
        "archivo": None,
        "drive_id": None,
        "url": None,
        "nota": "PENDIENTE DE GRABAR — día reservado",
    }]
    for i, (serie, it) in enumerate(orden):
        posts.append({
            "n": i + 2,
            "fecha": dias[i + 1].isoformat(),
            "hora": HORA,
            "serie": serie,
            "titulo": it["titulo"],
            "archivo": it["archivo"],
            "drive_id": it["drive_id"],
            "url": it["url"],
            "copy": "",
        })

    out = os.path.join(HUB, "ciclos/2026-09/xavi-colomina/programacion")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "videos.json"), "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    dias_es = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    mes_actual = None
    for p in posts:
        d = datetime.date.fromisoformat(p["fecha"])
        if d.strftime("%Y-%m") != mes_actual:
            mes_actual = d.strftime("%Y-%m")
            print(f"\n── {d.strftime('%B %Y').upper()} ──")
        print(f"{p['n']:>3}. {dias_es[d.weekday()]} {d.strftime('%d/%m')}  "
              f"[{p['serie']:<13}] {p['titulo']}")
    print(f"\n→ {out}/videos.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
