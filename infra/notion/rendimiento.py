#!/usr/bin/env python3
"""Base de Notion "📊 Rendimiento de vídeos" de un cliente, a partir del bruto de Metricool.

Pedido por Gerard el 28/09/2026 para Golossa, al estilo de la que ya tenía Xavi, pero
organizada por **las etiquetas del sistema** (Tipo de idea · Formato · Plantilla · Palanca).

Qué hace:
  1. Lee `memoria/metricas/_posts/<cliente>.json` (lo deja `fetch_metricool.py`). Usa el campo
     `copy` (entero); `texto` es solo la primera línea recortada para el resumen .md.
  2. **Junta en UNA pieza** el mismo vídeo publicado en Instagram y en TikTok (mismo copy y
     fechas a menos de 2 días). Sin esto, cada vídeo sale dos veces y todas las medias mienten.
  3. Calcula la NOTA de cada pieza: media geométrica de (vistas / mediana de su red) y
     (% de interacción / mediana de su red). Las vistas solas engañan — regla de Gerard del
     29/09/2026: 100k vistas al 1% valen menos que 50k al 10%. El veredicto sale de la NOTA.
  3b. Calculaba antes el veredicto solo contra la **mediana de su red** (mismo criterio que
     `infra/estado/termometro.py`: se compara con lo normal de ESE cliente, no con un absoluto).
  4. Crea la base en Notion y vuelca una fila por pieza.

⚠️ **Lo que NO rellena**: las etiquetas de contenido (Tipo de idea, Formato, Plantilla,
Palanca). El bruto de Metricool solo trae el copy y los números — no dice qué había en el
vídeo, y deducirlo del copy sería inventárselo. Esas columnas se crean vacías para que las
rellene una persona; a partir de ahí el análisis ya es medible.

Uso:
  rendimiento.py --cliente golossa --pagina <page_id> [--dry-run] [--desde YYYY-MM-DD]
  rendimiento.py --cliente golossa --db <database_id>        (vuelca en una base ya creada)
Salida: 0 ok · 2 falta token/config · 1 error
"""
import argparse
import datetime
import json
import os
import re
import statistics
import sys
import unicodedata

import notion_api as na

HUB = na.HUB
POSTS = os.path.join(HUB, "memoria/metricas/_posts")
PLANTILLAS_DIR = os.path.join(HUB, "agentes/guiones/plantillas")
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
# Mismo semáforo que el termómetro: ratio contra la mediana del cliente.
ESCALA = [(2.0, "🟢🟢 Pegó"), (1.2, "🟢 Por encima"), (0.8, "⚪ En su media"), (0.0, "🔴 Por debajo")]
# Listas cerradas: la fuente única es `agentes/guiones/ETIQUETAS.md` (se leen, no se copian).
sys.path.insert(0, os.path.join(na.HUB, "infra/analisis"))
import etiquetas as _etq  # noqa: E402  — lee las listas de agentes/guiones/ETIQUETAS.md
_L = _etq.listas()
TIPOS_IDEA, FORMATOS, PALANCAS = _L["Tipo de idea"], _L["Formato"], _L["Palanca"]


def normalizar(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(re.sub(r"#\w+|https?://\S+|[^a-z0-9 ]", " ", t).split())


def titulo_de(texto):
    """La primera línea con contenido del copy: es como Gerard reconoce la pieza."""
    for linea in (texto or "").splitlines():
        if linea.strip():
            return linea.strip()[:190]
    return "(sin copy)"


def agrupar(posts):
    """Una pieza = el mismo vídeo en varias redes (mismo arranque de copy, ±2 días)."""
    piezas = []
    for p in sorted(posts, key=lambda x: x["fecha"]):
        fecha = datetime.date.fromisoformat(p["fecha"])
        clave = normalizar(p.get("texto"))
        for g in piezas:
            n = min(25, len(g["clave"]), len(clave))
            if (n and g["clave"][:n] == clave[:n] and abs((g["fecha"] - fecha).days) <= 2
                    and p["red"] not in {x["red"] for x in g["posts"]}):
                g["posts"].append(p)
                break
        else:
            piezas.append({"clave": clave, "fecha": fecha, "posts": [p]})
    return piezas


def listones(posts):
    """Mediana de vistas por red · formato (y por red), para saber qué es 'normal' aquí."""
    grupo, red = {}, {}
    for p in posts:
        grupo.setdefault(f"{p['red']} · {p['formato']}", []).append(p.get("vistas", 0))
        red.setdefault(p["red"], []).append(p.get("vistas", 0))
    med = lambda xs: statistics.median(xs) if xs else 0  # noqa: E731
    return ({k: med(v) for k, v in grupo.items() if len(v) >= 4}, {k: med(v) for k, v in red.items()})


def liston_engagement(posts):
    """Mediana del % de interacción (interacciones/vistas) por red.

    Regla de Gerard (29/09/2026): **las vistas solas engañan**. 100.000 vistas con un 1% de
    interacción valen menos que 50.000 con un 10%: la segunda pieza conecta, la primera solo
    la empujó el algoritmo. Por eso cada pieza se mide en dos ejes y la NOTA los junta.
    """
    por_red = {}
    for p in posts:
        v = p.get("vistas", 0)
        if v:
            por_red.setdefault(p["red"], []).append(p.get("interacciones", 0) / v)
    return {k: (statistics.median(v) or 0) for k, v in por_red.items()}


def veredicto(ratio):
    for corte, texto in ESCALA:
        if ratio >= corte:
            return texto
    return "🔴 Por debajo"


def fila(pieza, grupos, redes, eng_red):
    ig = next((p for p in pieza["posts"] if p["red"] == "Instagram"), None)
    tt = next((p for p in pieza["posts"] if p["red"] == "TikTok"), None)
    # `copy` es el copy entero; `texto` (una línea recortada) es el respaldo de los brutos viejos.
    texto = max(((p.get("copy") or p.get("texto") or "") for p in pieza["posts"]), key=len)
    vistas = sum(p.get("vistas", 0) for p in pieza["posts"])
    esperado = sum(grupos.get(f"{p['red']} · {p['formato']}") or redes.get(p["red"], 0)
                   for p in pieza["posts"])
    ratio = round(vistas / esperado, 2) if esperado else 0
    # Eje 2: cuánto interactúan los que SÍ la vieron, contra lo normal del cliente en esa red.
    inter = sum(p.get("interacciones", 0) for p in pieza["posts"])
    eng = (inter / vistas) if vistas else 0
    esperado_eng = statistics.mean([eng_red.get(p["red"], 0) for p in pieza["posts"]] or [0])
    ratio_eng = round(eng / esperado_eng, 2) if esperado_eng else 0
    # NOTA = media geométrica de los dos ejes: para destacar hay que alcance Y conectar.
    # Geométrica y no aritmética a propósito: así un 0 en un eje no se tapa con el otro.
    nota = round((ratio * ratio_eng) ** 0.5, 2) if (ratio and ratio_eng) else 0
    return {
        "titulo": titulo_de(texto),
        "fecha": pieza["fecha"].isoformat(),
        "dia": DIAS[pieza["fecha"].weekday()],
        # Soporte = pieza, no red: el "Vídeo" de TikTok es un Reel (ETIQUETAS.md, 02/10/2026).
        "soporte": {"Vídeo": "Reel"}.get((ig or tt)["formato"], (ig or tt)["formato"]) if (ig or tt) else "",
        "redes": [p["red"] for p in pieza["posts"]],
        "ig": ig, "tt": tt,
        "vistas": vistas, "ratio": ratio, "veredicto": veredicto(nota) if (esperado and esperado_eng) else "",
        "inter": inter, "eng": round(eng * 100, 2), "ratio_eng": ratio_eng, "nota": nota,
        "texto": texto,
        "hashtags": len(re.findall(r"#\w+", texto)),
        "largo": len(texto),
    }


def esquema(cliente=None):
    """Las columnas. Las de etiquetas van VACÍAS: las rellena una persona, no se deducen."""
    sel = lambda ops: {"select": {"options": [{"name": o} for o in ops]}}  # noqa: E731
    return {
        "Pieza": {"title": {}},
        "Fecha": {"date": {}},
        "Día": sel(DIAS),
        "Soporte": sel(["Reel", "Carrusel", "Story", "Imagen", "Vídeo largo"]),
        "Redes": {"multi_select": {"options": [{"name": r} for r in ("Instagram", "TikTok")]}},
        "Vistas totales": {"number": {"format": "number"}},
        "Vs su mediana": {"number": {"format": "number"}},
        "Interacciones totales": {"number": {"format": "number"}},
        "Interacción %": {"number": {"format": "number"}},
        "Vs interacción mediana": {"number": {"format": "number"}},
        "Nota": {"number": {"format": "number"}},
        "Veredicto": sel([t for _, t in ESCALA]),
        "Etiquetado por": sel(["Gerard (vio el vídeo)", "Gemini (vídeo)", "Deducido del guion",
                               "Deducido del copy"]),
        "Por qué funciona (vídeo)": {"rich_text": {}},   # lo escribe infra/analisis/ver_video.py
        "IG Vistas": {"number": {"format": "number"}},
        "IG Alcance": {"number": {"format": "number"}},
        "IG Interacciones": {"number": {"format": "number"}},
        "IG Guardados": {"number": {"format": "number"}},
        "IG Engagement %": {"number": {"format": "number"}},
        "IG URL": {"url": {}},
        "TT Vistas": {"number": {"format": "number"}},
        "TT Alcance": {"number": {"format": "number"}},
        "TT Interacciones": {"number": {"format": "number"}},
        "TT Engagement %": {"number": {"format": "number"}},
        "TT URL": {"url": {}},
        "Copy": {"rich_text": {}},
        "Nº hashtags": {"number": {"format": "number"}},
        "Longitud copy": {"number": {"format": "number"}},
        # --- A RELLENAR A MANO (no se deducen del bruto) ---
        "Tipo de idea": sel(TIPOS_IDEA),
        "Formato": sel(FORMATOS),
        "Plantilla": sel(sorted(f[:-3] for f in os.listdir(PLANTILLAS_DIR)
                                if f.endswith(".md") and not f.startswith(("_", "README")))),
        "Palanca": {"multi_select": {"options": [{"name": p} for p in PALANCAS]}},
        "Notas": {"rich_text": {}},
        **etiquetas_cliente(cliente),
    }


def etiquetas_cliente(cliente):
    """Columna propia del cliente (config/etiquetas.json → etiquetas_cliente), si la tiene."""
    ops = ((_etq.config().get("etiquetas_cliente") or {}).get(cliente) or {}).get("opciones") or []
    return {"Etiquetas del cliente": {"multi_select": {"options": [{"name": o} for o in ops]}}} if ops else {}


def props_de(f):
    def num(v):
        return {"number": round(v, 2) if isinstance(v, float) else v}
    p = {
        "Pieza": na.prop_title(f["titulo"]),
        "Fecha": na.prop_date(f["fecha"]),
        "Día": na.prop_select(f["dia"]),
        "Redes": na.prop_multi(f["redes"]),
        "Vistas totales": num(f["vistas"]),
        "Copy": na.prop_text(f["texto"][:1900]),
        "Nº hashtags": num(f["hashtags"]),
        "Longitud copy": num(f["largo"]),
    }
    if f["soporte"]:
        p["Soporte"] = na.prop_select(f["soporte"])
    if f["veredicto"]:
        p["Veredicto"] = na.prop_select(f["veredicto"])
        p["Vs su mediana"] = num(f["ratio"])
        p["Vs interacción mediana"] = num(f["ratio_eng"])
        p["Nota"] = num(f["nota"])
    p["Interacciones totales"] = num(f["inter"])
    p["Interacción %"] = num(f["eng"])
    for red, pref in (("ig", "IG"), ("tt", "TT")):
        post = f[red]
        if not post:
            continue
        p[f"{pref} Vistas"] = num(post.get("vistas", 0))
        p[f"{pref} Alcance"] = num(post.get("alcance", 0))
        p[f"{pref} Interacciones"] = num(post.get("interacciones", 0))
        p[f"{pref} Engagement %"] = num(post.get("engagement", 0))
        if post.get("url"):
            p[f"{pref} URL"] = na.prop_url(post["url"])
        if red == "ig":
            p["IG Guardados"] = num(post.get("guardados", 0))
    return p


def analizar(db, tok, solo_gerard=False):
    """Qué etiqueta funciona, con la NOTA (vistas + interacción) y el nº de piezas detrás.

    Separa lo etiquetado por Gerard (vio el vídeo) de lo deducido del copy, porque no valen
    igual: lo segundo es una aproximación y hay que poder excluirlo.
    """
    filas = []
    for pg in na.query(db, tok):
        p = pg["properties"]
        def lst(k):
            v = na.plain(p.get(k))
            return v if isinstance(v, list) else ([v] if v else [])
        filas.append({
            "nota": (p.get("Nota") or {}).get("number"),
            "vistas": (p.get("Vistas totales") or {}).get("number") or 0,
            "eng": (p.get("Interacción %") or {}).get("number") or 0,
            "fuente": na.plain(p.get("Etiquetado por")) or "",
            "titulo": na.plain(p.get("Pieza")),
            **{c: lst(c) for c in ("Tipo de idea", "Formato", "Plantilla", "Palanca")},
        })
    if solo_gerard:
        filas = [f for f in filas if f["fuente"].startswith("Gerard")]
    L = [f"🔎 {len(filas)} piezas analizadas"
         f"{' (solo las que etiquetó Gerard)' if solo_gerard else ''}", ""]
    base = [f["nota"] for f in filas if f["nota"]]
    mediana_global = statistics.median(base) if base else 0
    L.append(f"Nota mediana de todas: {round(mediana_global, 2)} "
             f"(1.0 = una pieza normal de este cliente en vistas Y en interacción)")
    for campo in ("Tipo de idea", "Formato", "Plantilla", "Palanca"):
        acum = {}
        for f in filas:
            if not f["nota"]:
                continue
            for v in f[campo] or ["(sin etiqueta)"]:
                acum.setdefault(v, []).append(f["nota"])
        if not acum:
            continue
        L += ["", f"── {campo} ──"]
        for v, notas in sorted(acum.items(), key=lambda kv: statistics.median(kv[1]), reverse=True):
            m = round(statistics.median(notas), 2)
            aviso = "  ⚠️ pocas piezas" if len(notas) < 4 else ""
            L.append(f"  {veredicto(m)[:2]} {v[:38]:38} nota {m:<6} sobre {len(notas):>3} piezas{aviso}")
    return L


def actualizar(db, tok, filas, cliente=None):
    """Refresca métricas y NOTA de las filas que ya existen, casando por URL. No toca etiquetas.

    Se usa cuando cambian los números (métricas nuevas) o el cálculo (p. ej. al añadir la NOTA
    de interacción el 29/09/2026), sin rehacer la base y perder lo etiquetado a mano.
    """
    na._request("PATCH", f"/databases/{db}", tok, {"properties": {
        k: v for k, v in esquema(cliente).items()
        if k in ("Interacciones totales", "Interacción %", "Vs interacción mediana", "Nota",
                 "Etiquetado por", "Por qué funciona (vídeo)")}})
    por_url = {}
    for f in filas:
        for red in ("ig", "tt"):
            if f[red] and f[red].get("url"):
                por_url[f[red]["url"]] = f
    hechas, sin_casar, vistas_urls = 0, 0, set()
    for pg in na.query(db, tok):
        props = pg["properties"]
        f = None
        for k in ("IG URL", "TT URL"):
            u = (props.get(k) or {}).get("url")
            if u:
                vistas_urls.add(u)
            if u and u in por_url:
                f = por_url[u]
                break
        if not f:
            sin_casar += 1
            continue
        etiquetada = any((props.get(k) or {}).get("multi_select")
                         for k in ("Tipo de idea", "Formato", "Plantilla", "Palanca"))
        nuevas = props_de(f)
        # Solo métricas: las etiquetas de contenido no se tocan nunca desde aquí.
        nuevas = {k: v for k, v in nuevas.items()
                  if k in ("Vistas totales", "Vs su mediana", "Veredicto", "Nota",
                           "Interacciones totales", "Interacción %", "Vs interacción mediana")}
        if etiquetada and not (props.get("Etiquetado por") or {}).get("select"):
            nuevas["Etiquetado por"] = na.prop_select("Gerard (vio el vídeo)")
        try:
            na.update_props(pg["id"], tok, nuevas)
            hechas += 1
            if hechas % 50 == 0:
                print(f"  {hechas}…")
        except RuntimeError as e:
            sys.stderr.write(f"✗ {(props.get('Pieza') or {})}: {e}\n")
    # Upsert (02/10/2026): los vídeos publicados desde la última vez entran como filas nuevas,
    # sin etiquetas (las pone ver_video.py). Sin esto la base se quedaba congelada el día que se creó.
    nuevas_filas = [f for f in filas
                    if not any(f[r] and f[r].get("url") in vistas_urls for r in ("ig", "tt"))]
    for f in nuevas_filas:
        try:
            na.create_page(db, tok, props_de(f))
        except RuntimeError as e:
            sys.stderr.write(f"✗ nueva {f['fecha']} {f['titulo'][:40]}: {e}\n")
    print(f"✓ {hechas} filas actualizadas · {len(nuevas_filas)} nuevas · {sin_casar} sin casar por URL")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Base de rendimiento de vídeos en Notion.")
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--pagina", help="Page id de Notion donde crear la base.")
    ap.add_argument("--db", help="Database id ya creada (para volcar sin crear).")
    ap.add_argument("--desde", help="Solo piezas desde esta fecha (YYYY-MM-DD).")
    ap.add_argument("--actualizar", action="store_true",
                    help="Refresca métricas y NOTA de una base ya creada (--db). No toca etiquetas.")
    ap.add_argument("--analizar", action="store_true",
                    help="Cruza las etiquetas con la NOTA y dice qué funciona.")
    ap.add_argument("--solo-gerard", action="store_true",
                    help="Con --analizar: excluye lo etiquetado desde el copy.")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    try:
        with open(os.path.join(POSTS, f"{a.cliente}.json"), encoding="utf-8") as fh:
            datos = json.load(fh)
    except OSError:
        sys.stderr.write(f"No hay bruto de Metricool para {a.cliente}. Corre fetch_metricool.py.\n")
        return 2
    posts = datos["posts"]
    grupos, redes = listones(posts)
    piezas = agrupar(posts)
    eng_red = liston_engagement(posts)
    filas = [fila(p, grupos, redes, eng_red) for p in piezas]
    if a.desde:
        filas = [f for f in filas if f["fecha"] >= a.desde]
    filas.sort(key=lambda f: f["fecha"], reverse=True)
    print(f"{len(posts)} publicaciones -> {len(filas)} piezas "
          f"({sum(1 for f in filas if len(f['redes']) > 1)} en las dos redes)")
    if a.dry_run:
        for f in filas[:10]:
            print(f"  {f['fecha']} {f['veredicto']:15} x{f['ratio']:<6} {f['titulo'][:60]}")
        return 0

    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2

    if a.analizar:
        if not a.db:
            sys.stderr.write("--analizar necesita --db.\n")
            return 2
        print("\n".join(analizar(a.db, tok, a.solo_gerard)))
        return 0

    if a.actualizar:
        if not a.db:
            sys.stderr.write("--actualizar necesita --db.\n")
            return 2
        return actualizar(a.db, tok, filas, a.cliente)

    db = a.db
    if not db:
        if not a.pagina:
            sys.stderr.write("Dime --pagina (donde crearla) o --db (una ya creada).\n")
            return 2
        r = na._request("POST", "/databases", tok, {
            "parent": {"type": "page_id", "page_id": a.pagina},
            "title": [{"text": {"content": f"📊 Rendimiento de vídeos — {a.cliente}"}}],
            "properties": esquema(a.cliente),
        })
        db = r["id"]
        print(f"Base creada: {r.get('url')}")

    hechas = 0
    for f in filas:
        try:
            na.create_page(db, tok, props_de(f))
            hechas += 1
            if hechas % 25 == 0:
                print(f"  {hechas}/{len(filas)}…")
        except RuntimeError as e:
            sys.stderr.write(f"✗ {f['fecha']} {f['titulo'][:40]}: {e}\n")
    print(f"✓ {hechas}/{len(filas)} piezas volcadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
