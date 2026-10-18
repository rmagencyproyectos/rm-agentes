#!/usr/bin/env python3
"""Programa UNA pieza en Metricool según su formato y las redes conectadas de la marca.

Diseñado para que lo llame la app Project Pocket "al instante" al pulsar Programar
(el servidor Node ejecuta este script con /usr/bin/python3 y le pasa un JSON por stdin).

Reglas de negocio (corregidas 30/07/2026, WhatsApp de Gerard):
  - Reel     → Instagram + TikTok + YouTube + Facebook   (YT/FB con título SEO)
  - Story    → Instagram
  - Carrusel → Instagram (post) + TikTok + Facebook
  ADAPTATIVO: se publica solo en la intersección {redes deseadas} ∩ {redes conectadas de
  la marca}. Las redes deseadas que la marca NO tiene conectadas se ignoran en silencio
  (decisión de Gerard: no avisar de lo que no está conectado). Los ERRORES de la API sí
  se reportan (para que el llamador avise por WhatsApp con Winy).

Seguridad (Gate 3): por defecto DRY-RUN. No toca Metricool: solo calcula redes, arma el
payload real y lo devuelve. `--confirmar` crea BORRADOR; `--publicar` programa en firme.

Entrada (JSON por stdin o --in fichero):
  {
    "notionDb":  "c8ac7335-...",        # id de base Notion del cliente (join fiable), o
    "clientId":  "golossa",              # alias corto de la app (fallback), o
    "brandId":   5380508,                # brand_id de Metricool directo (fallback)
    "format":    "Reel|Story|Carrusel",
    "datetime":  "2026-08-02T15:00:00",  # hora local Europe/Madrid
    "copy":      "texto del post…",
    "driveUrl":  "https://drive.google.com/file/d/<ID>/view",  # vídeo final (reel/story)
    "title":     "Título SEO con gancho"  # para YouTube/Facebook
  }

Salida: JSON por stdout con {ok, dryRun, brand, targets, connected, skipped, results, payload}.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
API = "https://app.metricool.com/api"
TZ = "Europe/Madrid"

# Redes deseadas por formato (antes de intersecar con lo conectado).
DESIRED = {
    "Reel":     {"instagram", "tiktok", "youtube", "facebook"},
    "Story":    {"instagram"},
    "Carrusel": {"instagram", "tiktok", "facebook"},
}
# networksData de Metricool: clave -> nombre de red normalizado.
NET_KEY = {
    "instagramData": "instagram", "tiktokData": "tiktok", "facebookData": "facebook",
    "youtubeData": "youtube", "linkedinData": "linkedin", "twitterData": "twitter",
    "threadsData": "threads", "pinterestData": "pinterest", "gmbData": "gmb",
}


def load_env():
    env = {}
    with open(os.path.join(HUB, "infra/.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


def brand_map():
    """notionDb / clientId / brand_id -> {slug, brand_id, label}. Une los dos configs del hub."""
    marcas = json.load(open(os.path.join(HUB, "config/metricool-marcas.json")))["roster_v1"]
    bases = json.load(open(os.path.join(HUB, "config/notion-bases.json")))["clientes"]
    # alias cortos que usa la app Pocket -> slug del hub
    alias = {"jesus": "jesus-mora", "xavi": "xavi-colomina"}
    by_db, by_slug, by_brand = {}, {}, {}
    for slug, m in marcas.items():
        rec = {"slug": slug, "brand_id": m["brand_id"], "label": m["label"],
               "instagram": m.get("instagram", "")}
        by_slug[slug] = rec
        by_brand[str(m["brand_id"])] = rec
        db = bases.get(slug, {}).get("database_id")
        if db:
            by_db[db.replace("-", "")] = rec
    return by_db, by_slug, by_brand, alias


def resolve_brand(inp):
    by_db, by_slug, by_brand, alias = brand_map()
    if inp.get("brandId"):
        r = by_brand.get(str(inp["brandId"]))
        if r:
            return r
        # brandId fuera del roster (p. ej. la cuenta propia RM Agency): úsalo directo.
        return {"slug": "(brandId-directo)", "brand_id": int(inp["brandId"]),
                "label": f"brandId {inp['brandId']}", "instagram": ""}
    if inp.get("notionDb"):
        r = by_db.get(str(inp["notionDb"]).replace("-", ""))
        if r:
            return r
    cid = inp.get("clientId")
    if cid:
        cid = alias.get(cid, cid)
        r = by_slug.get(cid)
        if r:
            return r
    return None


def api_get(path, tok):
    r = urllib.request.Request(API + path, headers={"X-Mc-Auth": tok, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=40) as resp:
        return json.loads(resp.read().decode())


def connected_networks(brand_id, uid, tok):
    """Redes realmente conectadas en la marca (lee networksData de /v2/settings/brands)."""
    qs = urllib.parse.urlencode({"userToken": tok, "userId": uid, "blogId": brand_id})
    data = api_get(f"/v2/settings/brands?{qs}", tok)
    brands = data.get("data", data)
    obj = next((b for b in brands if str(b.get("id")) == str(brand_id)), None)
    if not obj:
        return set()
    nd = obj.get("networksData", {}) or {}
    out = set()
    for key, val in nd.items():
        if key in NET_KEY and val not in ("", None, False, 0):
            out.add(NET_KEY[key])
    return out


def parse_drive_id(url):
    if not url:
        return ""
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", url) or re.search(r"[?&]id=([A-Za-z0-9_-]{20,})", url)
    return m.group(1) if m else ""


def subir_imagenes(env, brand_id, images):
    """Sube una lista de imágenes (para carruseles) y devuelve sus fileUrl de Metricool.
    Cada entrada puede ser: ruta local a un archivo, URL http(s), o un id de Google Drive."""
    import mimetypes
    sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
    import subir_media
    urls = []
    for it in images:
        if isinstance(it, str) and os.path.exists(it):
            data = open(it, "rb").read()
            name = os.path.basename(it)
            ctype = mimetypes.guess_type(name)[0] or "image/png"
        elif isinstance(it, str) and it.startswith("http"):
            with urllib.request.urlopen(it, timeout=120) as r:
                data = r.read()
            name = it.rsplit("/", 1)[-1] or "imagen.jpg"
            ctype = mimetypes.guess_type(name)[0] or "image/jpeg"
        else:  # id de Drive
            data, name, ctype = subir_media.descargar_de_drive(env, it)
            if not (ctype or "").startswith("image/"):
                ctype = mimetypes.guess_type(name)[0] or "image/jpeg"
        urls.append(subir_media.subir_a_metricool(env, brand_id, data, name, ctype))
    return urls


def per_network_data(fmt, title):
    """Bloques *Data específicos por red según el formato."""
    d = {}
    if fmt == "Reel":
        d["instagramData"] = {"type": "REEL"}
        d["facebookData"] = {"type": "REEL"}
        d["youtubeData"] = {"title": title or "", "type": "SHORT"}
    elif fmt == "Story":
        d["instagramData"] = {"type": "STORY"}
    elif fmt == "Carrusel":
        d["instagramData"] = {"type": "POST"}
        d["facebookData"] = {"type": "POST"}
    return d


def build_payload(inp, brand, targets, media_urls, publicar):
    fmt = inp["format"]
    payload = {
        "text": inp.get("copy") or inp.get("title") or "",
        "publicationDate": {"dateTime": inp["datetime"], "timezone": TZ},
        "providers": [{"network": n} for n in sorted(targets)],
        "draft": not publicar,
        "autoPublish": bool(publicar),
    }
    if media_urls:
        payload["media"] = media_urls
    # Adjuntar solo los *Data de las redes que están en targets.
    for key, val in per_network_data(fmt, inp.get("title", "")).items():
        net = NET_KEY.get(key)
        if net in targets:
            payload[key] = val
    return payload


def crear_post(env, brand_id, uid, tok, payload):
    q = f"blogId={brand_id}&userId={uid}"
    req = urllib.request.Request(
        f"{API}/v2/scheduler/posts?{q}",
        data=json.dumps(payload).encode(),
        headers={"X-Mc-Auth": tok, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode(errors="replace")
            try:
                data = json.loads(body)
            except Exception:
                data = {"raw": body[:300]}
            return True, resp.status, data
    except urllib.error.HTTPError as e:
        return False, e.code, {"error": e.read().decode(errors="replace")[:400]}
    except Exception as e:  # noqa: BLE001
        return False, 0, {"error": str(e)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", help="Fichero JSON de entrada (si no, stdin)")
    p.add_argument("--confirmar", action="store_true", help="Crea BORRADOR en Metricool")
    p.add_argument("--publicar", action="store_true", help="Programa en firme (no borrador)")
    a = p.parse_args()

    raw = open(a.infile).read() if a.infile else sys.stdin.read()
    inp = json.loads(raw)
    out = {"ok": False, "dryRun": not (a.confirmar or a.publicar)}

    fmt = inp.get("format")
    if fmt not in DESIRED:
        out["error"] = f"Formato desconocido: {fmt!r} (esperado Reel/Story/Carrusel)"
        print(json.dumps(out, ensure_ascii=False)); return 2

    brand = resolve_brand(inp)
    if not brand:
        out["error"] = "No pude resolver la marca (notionDb/clientId/brandId no coincide con el roster)"
        print(json.dumps(out, ensure_ascii=False)); return 2
    out["brand"] = {"slug": brand["slug"], "brand_id": brand["brand_id"], "label": brand["label"]}

    env = load_env()
    tok, uid = env.get("METRICOOL_API_TOKEN"), env.get("METRICOOL_USER_ID")
    if not tok or not uid:
        out["error"] = "Faltan METRICOOL_API_TOKEN / METRICOOL_USER_ID en infra/.env"
        print(json.dumps(out, ensure_ascii=False)); return 2

    try:
        connected = connected_networks(brand["brand_id"], uid, tok)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"No pude leer redes conectadas: {e}"
        print(json.dumps(out, ensure_ascii=False)); return 1

    desired = DESIRED[fmt]
    targets = desired & connected
    out["connected"] = sorted(connected)
    out["desired"] = sorted(desired)
    out["targets"] = sorted(targets)
    out["skipped"] = sorted(desired - connected)  # informativo; NO se avisa de esto

    if not targets:
        out["error"] = "Ninguna red deseada está conectada en esta marca"
        print(json.dumps(out, ensure_ascii=False)); return 1

    drive_id = parse_drive_id(inp.get("driveUrl", ""))
    out["driveId"] = drive_id
    images = inp.get("images") or []
    needs_video = fmt in ("Reel", "Story")
    if needs_video and not drive_id:
        out["warning"] = "Falta el vídeo de Drive (driveUrl); en real haría falta para reel/story"
    if fmt == "Carrusel" and not images:
        out["warning"] = "Carrusel sin imágenes: pasa `images` (rutas locales, URLs o ids de Drive)"

    # DRY-RUN: no sube nada. Arma el payload SIN media real (marcadores de lo que se subiría).
    if out["dryRun"]:
        if needs_video and drive_id:
            ph = ["<video_de_drive_se_subiría_aquí>"]
        elif fmt == "Carrusel" and images:
            ph = [f"<imagen_{i+1}_se_subiría>" for i in range(len(images))]
        else:
            ph = []
        payload = build_payload(inp, brand, targets, ph, a.publicar)
        out["payload"] = payload
        out["ok"] = True
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0

    # REAL: consigue el media y crea el post. El vídeo de "Vídeo final" puede venir como
    # enlace de Google Drive, como URL ya alojada en Metricool (posts sincronizados) o como
    # cualquier otra URL http(s). Un reel/story SIN vídeo lo rechaza Metricool con un 400
    # opaco al programar en firme, así que lo obtenemos siempre (o avisamos claro).
    video_url = (inp.get("driveUrl") or "").strip()
    media_urls = []
    try:
        sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
        import subir_media
        if fmt == "Carrusel" and images:
            media_urls = subir_imagenes(env, brand["brand_id"], images)
        elif needs_video:
            if "static.metricool.com" in video_url:
                media_urls = [video_url]                       # ya alojado en Metricool: pásalo tal cual
            elif drive_id:
                media_urls = [subir_media.subir_video_de_drive(env, brand["brand_id"], drive_id)]
            elif video_url.startswith("http"):
                with urllib.request.urlopen(video_url, timeout=180) as r:
                    data = r.read()
                    ctype = r.headers.get("Content-Type") or "video/mp4"
                name = video_url.split("?")[0].rsplit("/", 1)[-1] or "video.mp4"
                media_urls = [subir_media.subir_a_metricool(env, brand["brand_id"], data, name, ctype)]
    except Exception as e:  # noqa: BLE001
        out["error"] = f"Subiendo media a Metricool: {e}"
        print(json.dumps(out, ensure_ascii=False)); return 1

    # Preflight: reel/story necesita vídeo. Sin él, avisamos claro en vez de un 400 opaco.
    if needs_video and not media_urls:
        out["error"] = (
            f"No pude obtener el vídeo de {video_url[:80]!r} (¿enlace de Drive sin acceso, o URL caída?). El {fmt} necesita vídeo."
            if video_url else
            f"El {fmt} no tiene vídeo en 'Vídeo final'. Añade el enlace antes de programar."
        )
        print(json.dumps(out, ensure_ascii=False)); return 1

    payload = build_payload(inp, brand, targets, media_urls, a.publicar)
    ok, status, data = crear_post(env, brand["brand_id"], uid, tok, payload)
    out["ok"] = ok
    out["httpStatus"] = status
    out["result"] = data
    out["mode"] = "publicado" if a.publicar else "borrador"
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
