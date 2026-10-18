#!/usr/bin/env python3
"""Creadores de referencia: de quién son los vídeos que guardamos como ejemplo, y qué les funciona.

Pedido por Gerard (02/10 y 08/10/2026): muchas ideas llegan con un vídeo de referencia. Oli
tiene que saber de QUÉ CREADOR es, usar ese creador (o parecidos) como modelo y conocer sus
mejores vídeos, no solo el que se guardó.

Qué hace, cada noche (dentro de infra/notion/noche.sh):
  1. Recorre las URLs de referencia de la Bandeja y de las bases de Contenido de cada cliente.
  2. Saca el @creador:
       - TikTok: de la URL (@usuario) o, si es un enlace corto, con yt-dlp (solo metadatos).
       - Instagram: si la URL lleva el usuario; si no, el que Gerard haya escrito en la columna
         «Creador ref». Instagram no se consulta (pediría la sesión de Gerard).
     Lo apunta en «Creador ref» de esa fila si estaba vacía.
  3. Por cada creador de TikTok: sus últimos ~60 vídeos con vistas (yt-dlp, sin descargar) →
     top 5 y la mediana. Se refresca una vez por semana.
  4. Gemini VE su mejor vídeo (una sola vez por creador) y dice por qué funciona y con qué
     formato/plantilla/palanca de ETIQUETAS.md. Lo descargado se borra al momento.
  5. Vuelca todo en la base de Notion «🎯 Creadores de referencia» (id en notion-bases.json →
     creadores_db) y escribe:
       memoria/analisis/creadores/<cliente>.md   lo que lee Oli al montar la tanda
       memoria/analisis/_creadores_pendientes.txt referencias de Instagram sin @creador → check-in
  Se excluyen las cuentas de nuestros propios clientes (un vídeo nuestro no es un referente).

Uso:  referencias.py [--dry-run] [--max-perfiles 8] [--max-gemini 5]
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import datetime
import json
import os
import re
import shutil
import statistics
import sys
import tempfile

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
sys.path.insert(0, os.path.join(HUB, "infra/analisis"))
import notion_api as na  # noqa: E402

SALIDA = os.path.join(HUB, "memoria/analisis")
CACHE = os.path.join(SALIDA, "creadores.json")
PENDIENTES = os.path.join(SALIDA, "_creadores_pendientes.txt")
AGENCIA_PAGE = "552067f9-114a-4e91-9f7d-27a0be9c9f33"   # «Agencia Marketing», donde vive la Bandeja
PROP_CREADOR = "Creador ref"
REFRESCO_DIAS = 7
# Pestaña «✍️ Falta el @» (Gerard, 08/10/2026): una fila por referencia de Instagram sin creador.
# Gerard cambia el nombre de la fila por el @; la noche siguiente se apunta en la idea de origen.
PLACEHOLDER = "✍️ Escribe aquí el @"
ESTADOS = ("Listo", "Falta el @", "Resuelta")
NO_ES_USUARIO = {"reel", "reels", "p", "tv", "stories", "explore"}


def hoy():
    return datetime.date.today().isoformat()


def cuentas_propias():
    """@ de nuestros clientes, sacados de sus propias publicaciones en Metricool."""
    propias = set()
    carpeta = os.path.join(HUB, "memoria/metricas/_posts")
    for f in os.listdir(carpeta):
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(carpeta, f), encoding="utf-8") as fh:
                for p in json.load(fh).get("posts", []):
                    m = re.search(r"tiktok\.com/@([\w.]+)", p.get("url") or "")
                    if m:
                        propias.add(m.group(1).lower())
        except (OSError, ValueError):
            continue
    return propias


def handle_de_url(url):
    m = re.search(r"tiktok\.com/@([\w.]+)", url)
    if m:
        return "TikTok", m.group(1)
    m = re.search(r"instagram\.com/([\w.]+)/(?:reel|p|tv)/", url)
    if m and m.group(1).lower() not in NO_ES_USUARIO:
        return "Instagram", m.group(1)
    return ("TikTok" if "tiktok" in url else "Instagram"), None


def handle_tiktok_ytdlp(url):
    import yt_dlp
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as y:
        i = y.extract_info(url, download=False)
    return i.get("uploader") or i.get("channel")


def perfil_tiktok(handle):
    """(top 5 [{url, vistas, titulo}], mediana de vistas) de sus últimos ~60 vídeos."""
    import yt_dlp
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True,
                           "extract_flat": True, "playlistend": 60}) as y:
        p = y.extract_info(f"https://www.tiktok.com/@{handle}", download=False)
    es = [e for e in (p.get("entries") or []) if e.get("view_count") is not None]
    if not es:
        return [], 0
    top = sorted(es, key=lambda e: -e["view_count"])[:5]
    return ([{"url": e.get("url"), "vistas": e["view_count"], "titulo": (e.get("title") or "")[:120]} for e in top],
            int(statistics.median(e["view_count"] for e in es)))


def analizar_mejor(cli, handle, video, listas, definiciones):
    """Gemini ve el mejor vídeo del creador. Descarga temporal, borrada al terminar."""
    import ver_video as V
    tmp = tempfile.mkdtemp(prefix="ref_")
    try:
        ruta = V.bajar_ytdlp(video["url"], tmp)
        prompt = ("Es un vídeo de REFERENCIA de otro creador (@" + handle + "), no de un cliente nuestro. "
                  "Lo que importa es POR QUÉ funciona, para copiar la mecánica.\n\n"
                  + V.prompt_para(listas, "@" + handle, video.get("titulo") or "", [], definiciones))
        res, _ = V.analizar(cli, ruta, prompt)
        lim = V.limpiar(res, listas, [])
        return {"por_que": res.get("por_que", ""), "gancho": res.get("gancho", ""),
                "formato": lim["Formato"], "plantilla": lim["Plantilla"], "palanca": lim["Palanca"],
                "tipo_idea": lim["Tipo de idea"]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- Notion
def asegurar_columna_creador(db, tok):
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    if PROP_CREADOR not in props:
        na._request("PATCH", f"/databases/{db}", tok, {"properties": {PROP_CREADOR: {"rich_text": {}}}})


def asegurar_base(cfg, tok, dry):
    if cfg.get("creadores_db"):
        return cfg["creadores_db"]
    if dry:
        return None
    ms = lambda ops: {"multi_select": {"options": [{"name": o} for o in ops]}}  # noqa: E731
    r = na._request("POST", "/databases", tok, {
        "parent": {"type": "page_id", "page_id": AGENCIA_PAGE},
        "title": [{"text": {"content": "🎯 Creadores de referencia"}}],
        "properties": {
            "Creador": {"title": {}}, "Red": {"select": {"options": [{"name": "TikTok"}, {"name": "Instagram"}]}},
            "Perfil": {"url": {}}, "Clientes": ms([]), "Veces referenciado": {"number": {"format": "number"}},
            "Mejor vídeo": {"url": {}}, "Vistas mejor vídeo": {"number": {"format": "number"}},
            "Mediana de vistas": {"number": {"format": "number"}}, "Top vídeos": {"rich_text": {}},
            "Por qué funciona": {"rich_text": {}}, "Gancho": {"rich_text": {}},
            "Formato": ms([]), "Plantilla": ms([]), "Palanca": ms([]), "Actualizado": {"date": {}},
        }})
    with open(os.path.join(HUB, "config/notion-bases.json"), encoding="utf-8") as f:
        todo = json.load(f)
    todo["creadores_db"] = r["id"]
    todo["_creadores_nota"] = ("creadores_db = base «🎯 Creadores de referencia» (08/10/2026). La llena "
                               "infra/olivia/referencias.py cada noche; Oli lee memoria/analisis/creadores/.")
    with open(os.path.join(HUB, "config/notion-bases.json"), "w", encoding="utf-8") as f:
        json.dump(todo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Base creada: {r.get('url')}")
    return r["id"]


def asegurar_columnas_base(db, tok):
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    nuevo = {}
    if "Estado" not in props:
        nuevo["Estado"] = {"select": {"options": [{"name": e} for e in ESTADOS]}}
    if "Referencia" not in props:
        nuevo["Referencia"] = {"url": {}}
    if "Idea" not in props:
        nuevo["Idea"] = {"url": {}}
    if nuevo:
        na._request("PATCH", f"/databases/{db}", tok, {"properties": nuevo})


def page_id_de(url):
    m = re.search(r"([0-9a-f]{32})(?:\?|$)", (url or "").replace("-", ""))
    return m.group(1) if m else None


def resolver_pendientes(db, tok, dry):
    """Filas «Falta el @» a las que Gerard ya les puso el @ en el nombre → se apunta en la idea de
    origen (columna «Creador ref») y la fila pasa a «Resuelta». Devuelve cuántas."""
    n = 0
    for pg in na.query(db, tok, {"property": "Estado", "select": {"equals": "Falta el @"}}):
        p = pg["properties"]
        nombre = (na.plain(p.get("Creador")) or "").strip()
        if not nombre or nombre == PLACEHOLDER:
            continue
        h = nombre.lstrip("@").split()[0]
        origen = page_id_de(na.plain(p.get("Idea")))
        if dry:
            print(f"  (dry-run) apuntaría @{h} en la idea {origen}")
            continue
        if origen:
            na.update_props(origen, tok, {PROP_CREADOR: na.prop_text("@" + h)})
        na.update_props(pg["id"], tok, {"Estado": na.prop_select("Resuelta"), "Creador": na.prop_title("@" + h)})
        n += 1
    return n


def volcar_pendientes(db, tok, sin_creador, labels):
    """Una fila «Falta el @» por referencia sin creador (sin duplicar: clave = URL de la referencia)."""
    ya = {na.plain(pg["properties"].get("Referencia")) for pg in na.query(
        db, tok, {"or": [{"property": "Estado", "select": {"equals": "Falta el @"}},
                         {"property": "Estado", "select": {"equals": "Resuelta"}}]})}
    nuevas = 0
    for r in sin_creador:
        if r["url"] in ya:
            continue
        na.create_page(db, tok, {
            "Creador": na.prop_title(PLACEHOLDER), "Estado": na.prop_select("Falta el @"),
            "Red": na.prop_select("Instagram"), "Referencia": na.prop_url(r["url"]),
            "Idea": na.prop_url(r["notion"]) if r.get("notion") else {"url": None},
            "Clientes": na.prop_multi([r["cliente"]]), "Por qué funciona": na.prop_text(
                f"Referencia guardada para {labels.get(r['cliente'], r['cliente'])}: «{r['idea'][:120]}». "
                "Abre el enlace de Referencia, mira de quién es y escribe su @ en el nombre de esta fila."),
            "Actualizado": na.prop_date(hoy()),
        })
        nuevas += 1
    return nuevas


def volcar(db, tok, handle, c, filas_existentes):
    t = lambda s: na.prop_text((s or "")[:1900])  # noqa: E731
    props = {
        "Creador": na.prop_title("@" + handle), "Red": na.prop_select(c["red"]),
        "Clientes": na.prop_multi(sorted(c["clientes"])), "Veces referenciado": {"number": c["veces"]},
        "Actualizado": na.prop_date(hoy()), "Estado": na.prop_select("Listo"),
    }
    if c.get("perfil"):
        props["Perfil"] = na.prop_url(c["perfil"])
    if c.get("top"):
        props["Mejor vídeo"] = na.prop_url(c["top"][0]["url"])
        props["Vistas mejor vídeo"] = {"number": c["top"][0]["vistas"]}
        props["Mediana de vistas"] = {"number": c.get("mediana") or 0}
        props["Top vídeos"] = t("\n".join(f"{v['vistas']:,} · {v['titulo'][:70]} · {v['url']}".replace(",", ".") for v in c["top"]))
    a = c.get("analisis") or {}
    if a:
        props["Por qué funciona"] = t(a.get("por_que"))
        props["Gancho"] = t(a.get("gancho"))
        for k, col in (("formato", "Formato"), ("plantilla", "Plantilla"), ("palanca", "Palanca")):
            if a.get(k):
                props[col] = na.prop_multi(a[k])
    pid = filas_existentes.get(handle.lower())
    if pid:
        na.update_props(pid, tok, props)
    else:
        na.create_page(db, tok, props)


# ---------------------------------------------------------------- salidas para Oli y el check-in
def escribir_md(creadores, labels, sin_creador):
    carpeta = os.path.join(SALIDA, "creadores")
    os.makedirs(carpeta, exist_ok=True)
    por_cliente = {}
    for h, c in creadores.items():
        for cl in c["clientes"]:
            por_cliente.setdefault(cl, []).append((h, c))
    for cl in set(list(por_cliente) + [s for s in labels]):
        lst = sorted(por_cliente.get(cl, []), key=lambda x: -x[1]["veces"])
        L = [f"# 🎯 Creadores de referencia — {labels.get(cl, cl)}", "",
             f"> Generado por `infra/olivia/referencias.py` · {hoy()}. Son los creadores de los vídeos que "
             "se han guardado como referencia para este cliente. Úsalos como modelo (o busca parecidos): "
             "su MEJOR vídeo dice qué mecánica les funciona, no solo el que se guardó.", ""]
        if not lst:
            L.append("(ninguna referencia con creador todavía)")
        for h, c in lst:
            L.append(f"## @{h} ({c['red']}) — referenciado {c['veces']} {'vez' if c['veces'] == 1 else 'veces'}")
            if c.get("top"):
                L.append(f"- Mediana de vistas: {c.get('mediana', 0):,}".replace(",", "."))
                for v in c["top"][:3]:
                    L.append(f"- {v['vistas']:,} vistas · {v['titulo'][:90]} · {v['url']}".replace(",", "."))
            a = c.get("analisis") or {}
            if a:
                etq = " · ".join(x for x in a.get("formato", []) + a.get("plantilla", []) + a.get("palanca", []))
                L.append(f"- Por qué funciona su mejor vídeo: {a.get('por_que', '')}")
                if a.get("gancho"):
                    L.append(f"- Gancho: {a['gancho']}")
                if etq:
                    L.append(f"- Etiquetas: {etq}")
            L.append("")
        pend = [p for p in sin_creador if p["cliente"] == cl]
        if pend:
            L += [f"## Referencias de Instagram sin @creador ({len(pend)})", ""]
            L += [f"- {p['url']}" for p in pend[:10]]
        with open(os.path.join(carpeta, f"{cl}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L).rstrip() + "\n")
    lineas = [f"generado {hoy()}"]
    if sin_creador:
        lineas.append(f"- {len(sin_creador)} referencias de Instagram sin @creador. Pestaña «✍️ Falta el @» de "
                      f"🎯 Creadores de referencia: cambia el nombre de cada fila por el @ y listo.")
        for p in sin_creador[:5]:
            lineas.append(f"  · {labels.get(p['cliente'], p['cliente'])}: {p['idea'][:60]} → {p['notion']}")
    with open(PENDIENTES, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(description="Creadores de los vídeos de referencia.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-perfiles", type=int, default=8)
    ap.add_argument("--max-gemini", type=int, default=5)
    a = ap.parse_args()
    try:
        tok = na.token()
    except RuntimeError as e:
        print(e)
        return 2
    cfg = na.load_config()
    labels = {s: c["label"] for s, c in cfg["clientes"].items()}
    propias = cuentas_propias()

    # 0. Lo que Gerard ya resolvió en la pestaña «✍️ Falta el @»
    if cfg.get("creadores_db"):
        asegurar_columnas_base(cfg["creadores_db"], tok)
        r = resolver_pendientes(cfg["creadores_db"], tok, a.dry_run)
        if r:
            print(f"✓ {r} referencias resueltas a mano (el @ ya está en su idea)")

    # 1-2. Referencias → creador
    bases = [("bandeja", cfg["bandeja"]["database_id"], None)]
    bases += [(s, c["database_id"], s) for s, c in cfg["clientes"].items()]
    creadores, sin_creador = {}, []
    try:
        with open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    for nombre, db, slug in bases:
        if not a.dry_run:
            asegurar_columna_creador(db, tok)
        for pg in na.query(db, tok):
            p = pg["properties"]
            cliente = slug or na.plain(p.get("Cliente")) or ""
            if cliente not in labels:
                continue
            urls = [v["url"] for k, v in p.items() if v["type"] == "url" and v.get("url") and k != "Vídeo final"
                    and re.search(r"tiktok\.com|instagram\.com", v["url"])]
            if not urls:
                continue
            manual = (na.plain(p.get(PROP_CREADOR)) or "").strip().lstrip("@").split()[0:1]
            for u in urls:
                red, h = handle_de_url(u)
                if not h and red == "TikTok":
                    try:
                        h = handle_tiktok_ytdlp(u)
                    except Exception as e:  # noqa: BLE001
                        print(f"  · no saco el creador de {u}: {str(e)[:80]}")
                if not h and manual:
                    h = manual[0]
                if not h:
                    sin_creador.append({"cliente": cliente, "url": u, "idea": na.plain(p.get("Idea")) or "",
                                        "notion": pg.get("url", "")})
                    continue
                if h.lower() in propias:
                    continue
                c = creadores.setdefault(h, {"red": red, "clientes": set(), "veces": 0,
                                             "perfil": f"https://www.{'tiktok.com/@' if red == 'TikTok' else 'instagram.com/'}{h}"})
                c["clientes"].add(cliente)
                c["veces"] += 1
                if not a.dry_run and not manual and PROP_CREADOR in p:
                    na.update_props(pg["id"], tok, {PROP_CREADOR: na.prop_text("@" + h)})
                    manual = [h]
    print(f"{len(creadores)} creadores · {len(sin_creador)} referencias de Instagram sin @creador")

    # 3. Perfiles de TikTok (cacheados una semana)
    hechos = 0
    for h, c in creadores.items():
        prev = cache.get(h, {})
        c.update({k: prev[k] for k in ("top", "mediana", "analisis", "perfil_fecha") if k in prev})
        if c["red"] != "TikTok" or hechos >= a.max_perfiles:
            continue
        viejo = (datetime.date.today() - datetime.date.fromisoformat(prev.get("perfil_fecha", "2000-01-01"))).days
        if viejo < REFRESCO_DIAS and prev.get("top"):
            continue
        try:
            c["top"], c["mediana"] = perfil_tiktok(h)
            c["perfil_fecha"] = hoy()
            hechos += 1
            print(f"  ✓ @{h}: {len(c['top'])} vídeos top · mediana {c['mediana']}")
        except Exception as e:  # noqa: BLE001
            print(f"  · @{h}: perfil no disponible ({str(e)[:80]})")

    # 4. Gemini ve el mejor vídeo de cada creador (una vez)
    if not a.dry_run:
        pend = [h for h, c in creadores.items() if c.get("top") and not c.get("analisis")][:a.max_gemini]
        if pend:
            import etiquetas as E
            import ver_video as V
            cli, listas, defs = V.cliente_gemini(), E.listas_automaticas(), E.definiciones()
            for h in pend:
                try:
                    creadores[h]["analisis"] = analizar_mejor(cli, h, creadores[h]["top"][0], listas, defs)
                    print(f"  ✓ Gemini vio el mejor vídeo de @{h}")
                except Exception as e:  # noqa: BLE001
                    print(f"  · Gemini no pudo con @{h}: {str(e)[:80]}")

    # 5. Notion + salidas
    if a.dry_run:
        for h, c in list(creadores.items())[:15]:
            print(f"  @{h} ({c['red']}) · {c['veces']}× · {sorted(c['clientes'])}")
        return 0
    db = asegurar_base(cfg, tok, a.dry_run)
    asegurar_columnas_base(db, tok)
    existentes = {(na.plain(pg["properties"].get("Creador")) or "").lstrip("@").lower(): pg["id"]
                  for pg in na.query(db, tok)
                  if na.plain(pg["properties"].get("Estado")) not in ("Falta el @", "Resuelta")}
    for h, c in creadores.items():
        try:
            volcar(db, tok, h, c, existentes)
        except RuntimeError as e:
            print(f"  ✗ Notion @{h}: {e}")
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({h: {**{k: v for k, v in c.items() if k != "clientes"}, "clientes": sorted(c["clientes"])}
                   for h, c in creadores.items()}, f, ensure_ascii=False, indent=1)
    nuevas = volcar_pendientes(db, tok, sin_creador, labels)
    if nuevas:
        print(f"✓ {nuevas} referencias nuevas en la pestaña «✍️ Falta el @»")
    escribir_md(creadores, labels, sin_creador)
    print(f"✓ {len(creadores)} creadores en Notion · fichas en memoria/analisis/creadores/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
