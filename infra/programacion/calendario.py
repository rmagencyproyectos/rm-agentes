#!/usr/bin/env python3
"""Reparte una lista de vídeos en el calendario de publicación del cliente.

Recibe los títulos de los vídeos EN EL ORDEN en que se quieren publicar (Gerard decide el orden;
este script no lo cambia) y los coloca en los próximos días de publicación del cliente según las
reglas canónicas — las MISMAS que usa el chequeo de cobertura (`infra/metricool/chequeo_cobertura.py`),
para no tener el calendario en dos sitios distintos.

Saca dos cosas:
  1) stdout: la lista CONCISA para reenviar al cliente. Solo "Día DD/MM — Título". Sin saludos,
     sin cierre, sin nada más (es lo que pidió Gerard: solo el calendario).
  2) --out <dir>/metricool.json: el payload de cada post (fecha, 15:00, las redes del cliente,
     brand_id) para que `infra/metricool/programar.py` lo suba a Metricool cuando Gerard dé el OK.
     Las redes salen de `config/metricool-marcas.json` (`redes` del cliente o `_redes_default`).
     Si el cliente publica en YouTube, cada vídeo necesita además `yt_titulo` en el videos.json.

Los títulos entran por stdin (uno por línea) o con --titulos-file.

Uso:
  calendario.py --cliente jesus-mora --desde 2026-07-29 --out ciclos/2026-07/jesus-mora/programacion < titulos.txt
"""
import argparse
import datetime
import json
import os
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
import chequeo_cobertura as cob  # noqa: E402  (REGLAS y DIAS_ES: fuente única del calendario)

MARCAS = os.path.join(HUB, "config/metricool-marcas.json")


def _marca(cliente):
    """Entrada del cliente en marcas.json (roster_v1 o fuera_de_roster_v1), o {}."""
    try:
        with open(MARCAS, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}, {}
    for grupo in ("roster_v1", "fuera_de_roster_v1"):
        entrada = (data.get(grupo) or {}).get(cliente)
        if isinstance(entrada, dict):
            return entrada, data
    return {}, data


def brand_id(cliente):
    """brand_id de Metricool del cliente. Vive en roster_v1/fuera_de_roster_v1 de marcas.json."""
    return _marca(cliente)[0].get("brand_id")


def redes_de(cliente):
    """Redes a las que publica el cliente. Fuente única: `redes` en config/metricool-marcas.json
    (si no la trae, `_redes_default`). Antes estaba escrito a mano aquí; se sacó el 21/08/2026 al
    añadir YouTube Shorts a Xavi, para no tener las redes en dos sitios."""
    entrada, data = _marca(cliente)
    return entrada.get("redes") or data.get("_redes_default") or ["instagram", "tiktok"]


def dias_publicacion(cliente, fecha=None):
    """Días de publicación del cliente. Con `fecha`, aplica pausas y excepciones temporales
    de `config/publicacion.json`; sin ella, devuelve la regla base."""
    if fecha is not None:
        return set(cob.dias_para(cliente, fecha).keys())
    return set(cob.REGLAS.get(cliente, cob.REGLAS["_default"])["dias"].keys())


def fechas_ocupadas(cliente, desde, hasta):
    """Días (date) que YA tienen algún post en Metricool en la ventana [desde, hasta].

    Sirve para no solapar: reutiliza `cob.get_programados` (la misma consulta del chequeo de
    cobertura). Si faltan credenciales o la API falla, devuelve set() y el reparto sigue como
    antes (no bloquea programar por un problema de red).
    """
    try:
        env = cob.load_env()
        tok, uid = env.get("METRICOOL_API_TOKEN"), env.get("METRICOOL_USER_ID")
        bid = brand_id(cliente)
        if not (tok and uid and bid):
            return set()
        posts = cob.get_programados(bid, uid, tok, desde, hasta)
    except Exception:
        return set()
    ocup = set()
    for p in posts or []:
        dt = (p.get("publicationDate") or {}).get("dateTime", "")
        try:
            ocup.add(datetime.datetime.fromisoformat(dt).date())
        except Exception:
            continue
    return ocup


def asignar_slots(cliente, desde, n, ocupadas=None):
    """Devuelve las n próximas fechas de publicación del cliente a partir de `desde`,
    saltando los días que ya tienen contenido programado en Metricool (`ocupadas`)."""
    ocupadas = ocupadas or set()
    fechas, d, tope = [], desde, desde + datetime.timedelta(days=365)
    while len(fechas) < n and d <= tope:
        # Se consulta día a día: durante una pausa el set viene vacío y no se asigna nada.
        if d.weekday() in dias_publicacion(cliente, d) and d not in ocupadas:
            fechas.append(d)
        d += datetime.timedelta(days=1)
    return fechas


def linea_concisa(fecha, titulo):
    return f"{cob.DIAS_ES[fecha.weekday()].capitalize()} {fecha:%d/%m} — {titulo}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cliente", required=True)
    p.add_argument("--desde", help="YYYY-MM-DD (por defecto, hoy)")
    p.add_argument("--titulos-file", help="Fichero con un título por línea (si no, stdin)")
    p.add_argument("--videos-json", help="JSON de listar_videos.py (lleva id de Drive → adjunta el "
                                          "vídeo al post). Si se usa, los títulos salen de ahí.")
    p.add_argument("--out", help="Directorio donde escribir metricool.json")
    p.add_argument("--ignorar-metricool", action="store_true",
                   help="No consultar Metricool para saltar días ocupados (tests).")
    a = p.parse_args()

    desde = datetime.date.fromisoformat(a.desde) if a.desde else datetime.date.today()
    # `items`: cada entrada = {"titulo", "drive_id", "copy"}. Con --videos-json llevamos el id de
    # Drive (para que programar.py adjunte el vídeo) y el `copy` de Coco (el texto real del post);
    # con títulos sueltos, drive_id/copy quedan None y el post sale con el título como texto.
    if a.videos_json:
        with open(a.videos_json, encoding="utf-8") as f:
            vids = json.load(f)
        items = [{"titulo": v.get("titulo", "").strip(),
                   "drive_id": v.get("id") or v.get("drive_id"),
                   "copy": (v.get("copy") or "").strip() or None,
                   "yt_titulo": (v.get("yt_titulo") or "").strip() or None}
                 for v in vids if v.get("titulo", "").strip()]
    else:
        if a.titulos_file:
            with open(a.titulos_file, encoding="utf-8") as f:
                lineas_in = [ln.strip() for ln in f if ln.strip()]
        else:
            lineas_in = [ln.strip() for ln in sys.stdin if ln.strip()]
        items = [{"titulo": t, "drive_id": None, "copy": None, "yt_titulo": None}
                 for t in lineas_in]
    if not items:
        sys.stderr.write("No hay vídeos/títulos que programar.\n")
        return 1

    # Para no solapar: preguntamos a Metricool qué días de la ventana ya tienen contenido y los
    # saltamos al repartir. Ventana amplia (medio año) para cubrir el stock que se esté programando.
    ocupadas = set()
    if not a.ignorar_metricool:
        ocupadas = fechas_ocupadas(a.cliente, desde, desde + datetime.timedelta(days=180))
        if ocupadas:
            sys.stderr.write(f"[Metricool: {len(ocupadas)} día(s) ya ocupados, se saltan]\n")

    fechas = asignar_slots(a.cliente, desde, len(items), ocupadas)
    if len(fechas) < len(items):
        sys.stderr.write(f"Aviso: solo cupieron {len(fechas)} de {len(items)} en un año.\n")

    bid = brand_id(a.cliente)
    redes = redes_de(a.cliente)
    posts = []
    lineas = []
    for fecha, item in zip(fechas, items):
        lineas.append(linea_concisa(fecha, item["titulo"]))
        post = {
            "fecha": fecha.isoformat(),
            "hora": "15:00",
            "titulo": item["titulo"],
            "redes": redes,
            "cliente": a.cliente,
            "brand_id": bid,
        }
        if item.get("drive_id"):
            post["drive_id"] = item["drive_id"]
        if item.get("copy"):
            post["texto"] = item["copy"]  # el copy de Coco = texto del post (si no, cae al título)
        if item.get("yt_titulo"):
            post["yt_titulo"] = item["yt_titulo"]  # YouTube exige título propio, no vale el copy
        posts.append(post)

    # 1) La lista concisa, tal cual, por stdout (para reenviar al cliente).
    sys.stdout.write("\n".join(lineas) + "\n")

    # 2) El payload para Metricool (gated: programar.py lo sube solo con el OK de Gerard).
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        destino = os.path.join(a.out, "metricool.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump({"cliente": a.cliente, "generado": datetime.date.today().isoformat(),
                       "posts": posts}, f, ensure_ascii=False, indent=2)
        sys.stderr.write(f"[metricool.json escrito en {destino} — pendiente de OK de Gerard]\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
