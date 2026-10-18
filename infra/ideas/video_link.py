#!/usr/bin/env python3
"""Saca título/descripción de un link de Instagram o TikTok — SIN descargar el vídeo.

Versión ligera (sin yt-dlp ni transcripción): pide los metadatos públicos del post para que
Winy tenga con qué redactar la idea. Para TikTok usa su oEmbed; para Instagram lee las
etiquetas OpenGraph de la página. Si no consigue nada, devuelve igual la URL para que la idea
se guarde con el link como referencia.

También deduce el SOPORTE de la pieza (Reel vs Carrusel; en Notion `Soporte`, que hasta el
22/09/2026 se llamaba "Formato"). Esto antes lo "decidía" el modelo,
que en la práctica ponía Reel a todo porque la plantilla del prompt lo llevaba escrito. Aquí es
determinista y gratis: la URL de Instagram ya lo dice casi siempre.

  /reel/ /reels/ /tv/  -> Reel   (certeza alta)
  /p/ con og:video     -> Reel   (vídeo de feed; certeza alta)
  /p/ sin og:video     -> Carrusel (post de feed; certeza media — puede ser una foto suelta)
  tiktok.com           -> Reel   (aguas abajo distribuir.py ya normaliza TikTok -> Reel)

Uso:  video_link.py "<url>"
Salida (stdout): JSON {"url","plataforma","titulo","descripcion","autor","soporte","certeza"}
(exit 0 siempre que la URL sea válida; los campos que no consiga van vacíos).
"""
import json
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def plataforma(url):
    u = url.lower()
    if "tiktok.com" in u:
        return "tiktok"
    if "instagram.com" in u:
        return "instagram"
    return "otra"


def _get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode(errors="replace")


def _og(html, prop):
    """Valor de un <meta property="og:PROP" content="..."> (o name=)."""
    for attr in ("property", "name"):
        m = re.search(
            r'<meta[^>]+%s=["\']og:%s["\'][^>]+content=["\']([^"\']*)["\']' % (attr, prop),
            html, re.I)
        if m:
            return m.group(1).strip()
    return ""


def desde_tiktok(url):
    try:
        data = json.loads(_get("https://www.tiktok.com/oembed?url=" + urllib.request.quote(url, safe=":/?=&")))
        return {"titulo": data.get("title", "") or "", "autor": data.get("author_name", "") or "",
                "descripcion": data.get("title", "") or ""}
    except Exception:
        return {}


def desde_og(url):
    try:
        html = _get(url)
    except Exception:
        return {}
    titulo = _og(html, "title")
    desc = _og(html, "description")
    # og:video solo aparece en piezas de vídeo; og:type es "video.*" en reels.
    es_video = bool(_og(html, "video") or _og(html, "video:secure_url")
                    or _og(html, "type").lower().startswith("video"))
    return {"titulo": titulo, "descripcion": desc, "autor": "", "_es_video": es_video}


def formato_desde_url(url, es_video=None):
    """(formato, certeza) a partir de la URL. `es_video` afina los /p/ ambiguos."""
    u = url.lower()
    if "tiktok.com" in u:
        return "Reel", "alta"
    if re.search(r"/(reel|reels|tv)/", u):
        return "Reel", "alta"
    if "/p/" in u:
        if es_video:
            return "Reel", "alta"
        # Post de feed sin señal de vídeo: casi siempre un carrusel. Si fuera una foto
        # suelta, Gerard lo corrige en Notion (y sigue siendo estático, no un Reel).
        return "Carrusel", "media"
    return "", ""


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        sys.stderr.write("uso: video_link.py <url>\n")
        return 1
    url = sys.argv[1].strip()
    plat = plataforma(url)
    info = {"url": url, "plataforma": plat, "titulo": "", "descripcion": "", "autor": "",
            "soporte": "", "certeza": ""}

    datos = {}
    if plat == "tiktok":
        datos = desde_tiktok(url) or desde_og(url)
    else:
        datos = desde_og(url)
    for k in ("titulo", "descripcion", "autor"):
        if datos.get(k):
            info[k] = datos[k]
    info["soporte"], info["certeza"] = formato_desde_url(url, datos.get("_es_video"))

    sys.stdout.write(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
