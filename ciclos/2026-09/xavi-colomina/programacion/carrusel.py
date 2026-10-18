#!/usr/bin/env python3
"""Sube a Metricool el carrusel de servicios de Xavi (7 slides 1080x1080) como UN post.

`programar.py` sirve para piezas de vídeo (un `drive_id` por post). Un carrusel es otra cosa:
N imágenes locales en un solo post, y sin YouTube (Shorts no admite carrusel). Por eso va aparte.

Las imágenes salen del proyecto de Claude Design "Carrusel de servicios Instagram"
(`Serveis Carrusel IG.dc.html`), exportadas a JPG por Gerard el 30/08/2026.

Uso:  carrusel.py --dir <carpeta con los jpg> [--confirmar]
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
API = "https://app.metricool.com/api"
TZ = "Europe/Madrid"
sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
sys.path.insert(0, os.path.join(HUB, "infra/programacion"))
import programar as pr      # noqa: E402  (ajustes de YouTube, tags, autopublicar)
import subir_media          # noqa: E402  (subida a Metricool, con multiparte)
import calendario as cal    # noqa: E402  (brand_id)

CLIENTE = "xavi-colomina"
FECHA = "2026-09-03"
HORA = "15:00"
# Un carrusel NO puede ir a YouTube Shorts: esta pieza es solo IG + TikTok, y por eso
# tampoco lleva `yt_titulo`. Es la excepción al `redes` del cliente en marcas.json.
REDES = ["instagram", "tiktok"]
COPY = os.path.join(HUB, "ciclos/2026-09/xavi-colomina/copies/00_carrusel-servicios.md")


def texto():
    return open(COPY, encoding="utf-8").read().split("---", 2)[2].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--confirmar", action="store_true")
    a = ap.parse_args()

    env = pr.load_env()
    bid = cal.brand_id(CLIENTE)
    jpgs = sorted(f for f in os.listdir(a.dir) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not jpgs:
        sys.stderr.write("No hay imágenes en esa carpeta.\n")
        return 1

    firme = pr.autopublica(CLIENTE)
    cuerpo = texto()
    print(f"Carrusel · {CLIENTE} · {FECHA} {HORA} · {'+'.join(REDES)} · {len(jpgs)} slides")
    for i, f in enumerate(jpgs, 1):
        print(f"  {i}. {f}")
    print(f"Copy: {len(cuerpo)} car. · Etiquetas: no aplica (sin YouTube)")
    print("🚨 EN FIRME: se publica solo a su hora." if firme else "Se crea como BORRADOR.")
    if not a.confirmar:
        print("\n(preview — no he tocado Metricool. Añade --confirmar.)")
        return 0

    media = []
    for f in jpgs:
        ruta = os.path.join(a.dir, f)
        datos = open(ruta, "rb").read()
        mime = "image/png" if f.lower().endswith(".png") else "image/jpeg"
        media.append(subir_media.subir_a_metricool(env, bid, datos, f, mime))
        print(f"  ↑ {f}  ({len(datos)/1024:.0f} KB)")

    payload = {
        "text": cuerpo,
        "publicationDate": {"dateTime": f"{FECHA}T{HORA}:00", "timezone": TZ},
        "providers": [{"network": n} for n in REDES],
        "media": media,
        "draft": not firme,
        "autoPublish": bool(firme),
        # Varias imágenes en un post de IG = carrusel. El tipo es POST, no REEL.
        "instagramData": {"type": "POST", "autoPublish": bool(firme)},
    }
    q = f"blogId={bid}&userId={env['METRICOOL_USER_ID']}"
    req = urllib.request.Request(
        f"{API}/v2/scheduler/posts?{q}", data=json.dumps(payload).encode(),
        headers={"X-Mc-Auth": env["METRICOOL_API_TOKEN"], "Content-Type": "application/json",
                 "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode() or "{}")
            pid = (d.get("data") or d).get("id")
            print(f"\n✅ creado · id={pid} · "
                  f"https://app.metricool.com/planning/list?blogId={bid}&postId={pid}")
            return 0
    except urllib.error.HTTPError as e:
        print(f"\n❌ {e.code}: {e.read().decode(errors='replace')[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
