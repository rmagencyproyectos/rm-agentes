#!/usr/bin/env python3
"""Sube un artículo del blog de RM a rmagency.es (WordPress) — en BORRADOR por defecto.

Uso:
  /usr/bin/python3 infra/web/blog.py <articulo.md> [--imagen portada.png] [--dry-run]
  /usr/bin/python3 infra/web/blog.py <articulo.md> --actualizar <post_id>   # rehace el borrador
  /usr/bin/python3 infra/web/blog.py --publicar <post_id>                   # solo con «publica» de Gerard

El .md lleva frontmatter (titulo_seo, slug, meta_description, imagen_destacada, categoria) y el
cuerpo en Markdown sencillo (#, ##, párrafos, **negrita**, listas «- » y «1. »). Se convierte a
bloques del editor de WordPress, así el artículo se puede retocar a mano en WP.

Credenciales en infra/.env (las pone Gerard, nunca un agente): WP_URL, WP_USER, WP_APP_PASSWORD
(contraseña de aplicación; en Hostinger hay que tener APAGADO «Desactivar las contraseñas de las
aplicaciones» en Hostinger → Herramientas → Seguridad). Montado el 14/10/2026.
Gate: igual que Metricool — esto deja BORRADORES; publicar solo si Gerard dice «publica».
"""
import argparse
import base64
import html
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"


def load_env():
    env = {}
    with open(os.path.join(HUB, "infra/.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    for k in ("WP_URL", "WP_USER", "WP_APP_PASSWORD"):
        if not env.get(k):
            sys.exit(f"Falta {k} en infra/.env")
    return env


class WP:
    def __init__(self, env, usuario=None):
        self.base = env["WP_URL"].rstrip("/") + "/wp-json/wp/v2"
        cred = f"{usuario or env['WP_USER']}:{env['WP_APP_PASSWORD']}"
        self.auth = "Basic " + base64.b64encode(cred.encode()).decode()

    def pedir(self, metodo, ruta, datos=None, cuerpo=None, cabeceras=None):
        h = {"Authorization": self.auth, "Accept": "application/json"}
        if datos is not None:
            cuerpo = json.dumps(datos).encode()
            h["Content-Type"] = "application/json"
        h.update(cabeceras or {})
        req = urllib.request.Request(self.base + ruta, data=cuerpo, method=metodo, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            sys.exit(f"WordPress {e.code} en {metodo} {ruta}: {e.read().decode(errors='replace')[:300]}")

    def subir_imagen(self, ruta):
        nombre = os.path.basename(ruta)
        tipo = mimetypes.guess_type(ruta)[0] or "image/png"
        m = self.pedir("POST", "/media", cuerpo=open(ruta, "rb").read(), cabeceras={
            "Content-Type": tipo, "Content-Disposition": f'attachment; filename="{nombre}"'})
        return m["id"]

    def categoria(self, nombre):
        q = urllib.parse.quote(nombre)
        for c in self.pedir("GET", f"/categories?search={q}&per_page=20"):
            if html.unescape(c["name"]).lower() == nombre.lower():
                return c["id"]
        return self.pedir("POST", "/categories", {"name": nombre})["id"]


def leer(md_path):
    texto = open(md_path, encoding="utf-8").read()
    meta, cuerpo = {}, texto
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if m:
        for linea in m.group(1).splitlines():
            if ":" in linea:
                k, v = linea.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        cuerpo = m.group(2)
    return meta, cuerpo


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2">\1</a>', t)
    return t


def a_bloques(md):
    """Markdown sencillo → bloques Gutenberg. Devuelve (h1, html)."""
    h1, out, lista, tipo = None, [], [], None

    def cerrar_lista():
        nonlocal lista, tipo
        if lista:
            ordenada = tipo == "ol"
            attrs = ' {"ordered":true}' if ordenada else ""
            items = "".join(f"<!-- wp:list-item --><li>{i}</li><!-- /wp:list-item -->" for i in lista)
            out.append(f"<!-- wp:list{attrs} --><{tipo} class=\"wp-block-list\">{items}</{tipo}><!-- /wp:list -->")
        lista, tipo = [], None

    for bloque in re.split(r"\n\s*\n", md.strip()):
        for linea in bloque.splitlines():
            linea = linea.rstrip()
            if not linea:
                continue
            if linea.startswith("# "):
                cerrar_lista(); h1 = linea[2:].strip(); continue
            mh = re.match(r"^(#{2,4}) (.+)", linea)
            if mh:
                cerrar_lista(); n = len(mh.group(1))
                attrs = "" if n == 2 else f' {{"level":{n}}}'
                out.append(f"<!-- wp:heading{attrs} --><h{n} class=\"wp-block-heading\">{inline(mh.group(2))}</h{n}><!-- /wp:heading -->")
                continue
            mu = re.match(r"^[-*] (.+)", linea)
            mo = re.match(r"^\d+\. (.+)", linea)
            if mu or mo:
                t = "ul" if mu else "ol"
                if tipo and tipo != t:
                    cerrar_lista()
                tipo = t; lista.append(inline((mu or mo).group(1))); continue
            cerrar_lista()
            out.append(f"<!-- wp:paragraph --><p>{inline(linea)}</p><!-- /wp:paragraph -->")
        cerrar_lista()
    return h1, "\n\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("md", nargs="?")
    p.add_argument("--imagen", help="Imagen destacada (si no, la del frontmatter, junto al .md)")
    p.add_argument("--actualizar", type=int, help="Id de un borrador ya creado para rehacerlo")
    p.add_argument("--publicar", type=int, help="Publica un borrador ya revisado (solo con OK de Gerard)")
    p.add_argument("--programar", help="Fecha local YYYY-MM-DDTHH:MM: publica en esa fecha (WordPress lo programa)")
    p.add_argument("--usuario", help="Sobrescribe WP_USER (pruebas)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    env = load_env()
    wp = WP(env, a.usuario)

    if a.publicar:
        d = wp.pedir("POST", f"/posts/{a.publicar}", {"status": "publish"})
        print(f"✅ publicado: {d.get('link')}")
        return
    if not a.md:
        p.error("falta el .md")

    meta, cuerpo = leer(a.md)
    h1, contenido = a_bloques(cuerpo)
    titulo = h1 or meta.get("titulo_seo") or "Sin título"
    img = a.imagen or (os.path.join(os.path.dirname(a.md), meta["imagen_destacada"].split()[0])
                       if meta.get("imagen_destacada") else None)
    print(f"Título: {titulo}\nSlug: {meta.get('slug')}\nCategoría: {meta.get('categoria')}\n"
          f"Imagen: {img}\nBloques: {contenido.count('<!-- wp:')} · {len(re.sub('<[^>]+>', '', contenido).split())} palabras")
    if a.dry_run:
        return

    post = {"title": titulo, "content": contenido, "status": "draft",
            "excerpt": meta.get("meta_description", "")}
    if a.programar:  # solo con OK de Gerard («publícalos escalonados», 18/10/2026)
        post["status"], post["date"] = "future", a.programar + ":00"
    if meta.get("slug"):
        post["slug"] = meta["slug"]
    if meta.get("categoria"):
        post["categories"] = [wp.categoria(meta["categoria"])]
    if img and os.path.exists(img):
        post["featured_media"] = wp.subir_imagen(img)

    ruta = f"/posts/{a.actualizar}" if a.actualizar else "/posts"
    d = wp.pedir("POST", ruta, post)
    # SEO en Rank Math (instalado el 14/10/2026): palabra clave, título y descripción para Google.
    seo = {"rank_math_focus_keyword": meta.get("kw_principal", "").split("(")[0].strip(),
           "rank_math_description": meta.get("meta_description", ""),
           "rank_math_title": (meta.get("titulo_seo") or titulo) + " %sep% %sitename%"}
    req = urllib.request.Request(env["WP_URL"].rstrip("/") + "/wp-json/rankmath/v1/updateMeta",
                                 data=json.dumps({"objectType": "post", "objectID": d["id"], "meta": seo}).encode(),
                                 method="POST", headers={"Authorization": wp.auth, "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=60).read()
        print(f"   SEO (Rank Math): «{seo['rank_math_focus_keyword']}»")
    except urllib.error.HTTPError as e:
        print(f"   ⚠️ Rank Math no aceptó el SEO ({e.code}); el extracto queda como descripción.")
    print(f"✅ {'actualizado' if a.actualizar else 'creado'}: id {d['id']} · estado {d['status']} · fecha {d.get('date')}")
    print(f"   Editar: {env['WP_URL'].rstrip('/')}/wp-admin/post.php?post={d['id']}&action=edit")
    print(f"   Vista previa: {d.get('link')}")


if __name__ == "__main__":
    main()
