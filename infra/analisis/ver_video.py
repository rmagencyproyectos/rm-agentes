#!/usr/bin/env python3
"""Gemini VE cada vídeo publicado y le pone las etiquetas comunes. Pedido por Gerard, 02/10/2026.

Por qué: etiquetar por el copy es adivinar (Golossa: 214 de 253 filas "Deducido del copy").
Gemini entiende imagen + audio del vídeo entero, así que la etiqueta sale de lo que de verdad
pasa en pantalla.

Dónde busca el vídeo, de lo más exacto a lo menos:
  1. TikTok      — la URL ES ese vídeo. yt-dlp, público, sin login.
  2. Drive       — el "Vídeo final" que pega el editor en la ficha de Contenido (si es público).
  3. Disco       — /Volumes/DD 2 TB WORK/<cliente>/ , por parecido del nombre del archivo con el
                   título de la ficha. Como puede fallar, Gemini dice si el vídeo casa con el copy
                   y, si no, se descarta y se prueba la siguiente fuente.
  4. Instagram   — yt-dlp con la sesión de Chrome de Gerard (lo pidió él). Lo último y despacio,
                   para no castigar su cuenta.
Lo descargado va a una carpeta temporal que se BORRA al terminar cada vídeo (finally). Del disco
y de Drive solo se lee: nunca se borra ni se mueve nada.

Dónde escribe (config/etiquetas.json → etiquetas_viven_en):
  - rendimiento: en la propia fila (Golossa, Jesús, NewMos).
  - contenido:   en la ficha enlazada por "Pieza de producción" (Xavi).
  Siempre: "Etiquetado por = Gemini (vídeo)" y "Por qué funciona (vídeo)" en la fila de rendimiento.

Reglas:
  - Lo que puso Gerard NO se toca, nunca (02/10/2026: "si lo etiqueté a mano, ya está hecho").
  - `no_inferir` de etiquetas.json: opciones que Gemini no usa (Oficio: sale siempre, no distingue).
  - "Etiquetas del cliente": lista cerrada propia de cada cliente (`etiquetas_cliente`), en la
    fila de rendimiento. Solo se rellena si está vacía (en Xavi viene sembrada de su Tema).
  - Si ningún Formato encaja, Gemini lo deja vacío y propone uno ("formato_sugerido"): queda
    escrito en "Por qué funciona (vídeo)" para que Gerard decida si amplía la lista.
  - En la ficha de Contenido solo rellena lo vacío (la Plantilla de Coco es la mecánica real con
    la que se escribió el guion; no se pisa).
  - Solo opciones de las listas cerradas. Lo que Gemini devuelva fuera de lista se tira.

Uso:
  ver_video.py --cliente xavi-colomina [--max 10] [--dry-run] [--sin-ig] [--fila <page_id>]
  ver_video.py --cliente golossa --con-palanca Emoción --max 30     (reetiquetar las de Emoción)
Salida: 0 ok · 2 falta token/key · 3 cuota de Gemini agotada · 1 error
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
import notion_api as na  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etiquetas as E  # noqa: E402

# 2.5-flash ya no se da a cuentas nuevas (02/10/2026). En orden; si uno está saturado (503), el
# siguiente. Todos son Flash: barato y suficiente para etiquetar.
MODELOS = ("gemini-flash-latest", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash")
DISCO = "/Volumes/DD 2 TB WORK"
CARPETA_DISCO = {"xavi-colomina": "Xavi Colomina", "jesus-mora": "Jesus Mora", "golossa": "Golossa"}
ETQ_FUENTE = "Gemini (vídeo)"
COL_PORQUE = "Por qué funciona (vídeo)"
CAMPOS = ("Tipo de idea", "Formato", "Plantilla", "Palanca", "Soporte")
PAUSA_IG = 6          # segundos entre descargas de Instagram
USD_POR_VIDEO = 0.01  # orientativo: ~1 min de vídeo en Flash


def norm(t):
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return set(w for w in re.sub(r"[^a-z0-9 ]", " ", t).split() if len(w) > 2)


def cfg_etiquetas():
    """(config/etiquetas.json, listas sin lo de `no_inferir`, definiciones de ETIQUETAS.md)."""
    return E.config(), E.listas_automaticas(), E.definiciones()


# ---------------------------------------------------------------- fuentes de vídeo
def bajar_ytdlp(url, carpeta, ig=False):
    import yt_dlp
    opts = {"outtmpl": os.path.join(carpeta, "%(id)s.%(ext)s"), "format": "best[ext=mp4]/best",
            "quiet": True, "no_warnings": True, "noprogress": True}
    if ig:
        opts["cookiesfrombrowser"] = ("chrome",)
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(url, download=True)
        return y.prepare_filename(info)


def bajar_drive(url, carpeta):
    m = re.search(r"/d/([\w-]+)", url) or re.search(r"id=([\w-]+)", url)
    if not m:
        return None
    dest = os.path.join(carpeta, m.group(1) + ".mp4")
    req = urllib.request.Request(f"https://drive.google.com/uc?export=download&id={m.group(1)}&confirm=t",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        if "text/html" in r.headers.get("Content-Type", ""):
            return None   # no es público: Drive devuelve la página de login
        with open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
    return dest


def buscar_disco(slug, titulo, fecha):
    raiz = os.path.join(DISCO, CARPETA_DISCO.get(slug, ""))
    if not os.path.isdir(raiz) or slug not in CARPETA_DISCO:
        return None
    buscado = norm(titulo)
    if len(buscado) < 2:
        return None
    mejor, puntos = None, 0.0
    for d, _, fs in os.walk(raiz):
        for f in fs:
            if not f.lower().endswith((".mp4", ".mov")) or f.startswith("."):
                continue
            tiene = norm(os.path.splitext(f)[0])
            comun = len(buscado & tiene) / len(buscado)
            if "acabat" in d.lower() or "export" in d.lower():
                comun += 0.1
            if comun > puntos:
                mejor, puntos = os.path.join(d, f), comun
    return mejor if puntos >= 0.6 else None


# ---------------------------------------------------------------- Gemini
def cliente_gemini():
    from google import genai
    key = (na.load_env().get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip().strip('"')
    if not key:
        raise RuntimeError("Falta GEMINI_API_KEY en infra/.env")
    return genai.Client(api_key=key)


def prompt_para(listas, label, copy, propias, definiciones):
    L = {k: " | ".join(v) for k, v in listas.items()}
    glosario = definiciones
    extra = (',\n  "etiquetas_cliente": ["..."]   // 1-3 de: ' + " | ".join(propias)
             + " — de qué trata en concreto") if propias else ""
    return f"""Eres analista de contenido de RM Agency. Mira el vídeo entero (imagen y audio) de {label}.
Copy con el que se publicó: «{copy[:800]}»

Responde SOLO con un objeto JSON:
{{"coincide": true/false,        // ¿este vídeo es el del copy? Si claramente no, false
  "tipo_idea": ["..."],          // 1-2 de: {L["Tipo de idea"]}
  "formato": ["..."],            // 1-2 de: {L["Formato"]}. Si NINGUNO encaja de verdad, []
  "formato_sugerido": "",        // solo si formato está vacío: cómo llamarías a este formato
  "plantilla": "...",            // 1 de: {L["Plantilla"]}
  "palanca": ["..."],            // 1-2 de: {L["Palanca"]}
  "soporte": "...",              // 1 de: {L["Soporte"]}
  "gancho": "qué se ve y se oye en los 3 primeros segundos, 1 frase",
  "por_que": "por qué funciona o por qué no engancha, 2 frases concretas sobre ESTE vídeo",
  "confianza": 0.0-1.0{extra}}}
Usa SOLO valores de esas listas, escritos igual. Si nada encaja en un campo, déjalo vacío:
mejor vacío que forzado. tipo_idea describe el ÁNGULO del vídeo, no el sector del cliente:
una lección o un consejo técnico sin más ángulo lleva tipo_idea VACÍO (lo que enseña ya lo
dicen el formato y las etiquetas del cliente).

Qué significa cada opción y cómo desempatar (de la guía de la agencia; donde la guía mencione
una opción que no está en las listas de arriba, NO la uses):
{glosario}"""


class CuotaAgotada(RuntimeError):
    """Plan gratuito de Gemini: 20 peticiones/día por modelo. Seguir solo gasta intentos."""


def analizar(cli, ruta, prompt):
    """Con `ruta`: Gemini ve el vídeo. Con `ruta=None`: solo lee el texto del prompt (plan B, copy)."""
    from google.genai import types
    if ruta is None:
        for modelo in MODELOS:
            try:
                r = cli.models.generate_content(
                    model=modelo, contents=[prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2))
                return json.loads(r.text), modelo
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) and "free_tier" in str(e):
                    raise CuotaAgotada(str(e)) from e
                ultimo = e
        raise RuntimeError(f"Gemini: {str(ultimo)[:160]}")
    f = cli.files.upload(file=ruta)
    try:
        for _ in range(60):
            if f.state and f.state.name == "ACTIVE":
                break
            if f.state and f.state.name == "FAILED":
                raise RuntimeError("Gemini no pudo procesar el vídeo")
            time.sleep(3)
            f = cli.files.get(name=f.name)
        ultimo = None
        for intento in range(2):          # 2 vueltas a la lista, con espera: el 503 suele ser de minutos
            for modelo in MODELOS:
                try:
                    r = cli.models.generate_content(
                        model=modelo, contents=[f, prompt],
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2))
                    return json.loads(r.text), modelo
                except Exception as e:   # saturado / retirado: prueba el siguiente
                    if "RESOURCE_EXHAUSTED" in str(e) and "free_tier" in str(e):
                        raise CuotaAgotada(str(e)) from e
                    ultimo = e
            if intento == 0:
                time.sleep(20)
        raise RuntimeError(f"Gemini: {str(ultimo)[:160]}")
    finally:
        try:
            cli.files.delete(name=f.name)
        except Exception:
            pass


# ---------------------------------------------------------------- Notion
def asegurar_columnas(db, tok, multi):
    """Etiquetado por (con la opción Gemini) y Por qué funciona (vídeo). Idempotente."""
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    nuevo = {}
    if "Etiquetado por" not in props:
        nuevo["Etiquetado por"] = {"select": {"options": [{"name": "Gerard (vio el vídeo)"}, {"name": ETQ_FUENTE},
                                                          {"name": "Deducido del guion"}, {"name": "Deducido del copy"}]}}
    elif ETQ_FUENTE not in [o["name"] for o in props["Etiquetado por"]["select"]["options"]]:
        ops = props["Etiquetado por"]["select"]["options"] + [{"name": ETQ_FUENTE}]
        nuevo["Etiquetado por"] = {"select": {"options": [{"name": o["name"]} for o in ops]}}
    if multi and COL_PORQUE not in props:
        nuevo[COL_PORQUE] = {"rich_text": {}}
    if nuevo:
        na._request("PATCH", f"/databases/{db}", tok, {"properties": nuevo})
    return na._request("GET", f"/databases/{db}", tok)["properties"]


def valor_prop(esquema, campo, valores):
    p = esquema.get(campo)
    if not p or not valores:
        return None
    if p["type"] == "multi_select":
        return {"multi_select": [{"name": v} for v in valores]}
    if p["type"] == "select":
        return {"select": {"name": valores[0]}}
    return None


def limpiar(res, listas, propias):
    def lst(k, campo):
        v = res.get(k) or []
        v = v if isinstance(v, list) else [v]
        return [x for x in v if x in listas[campo]][:2]
    return {"Tipo de idea": lst("tipo_idea", "Tipo de idea"), "Formato": lst("formato", "Formato"),
            "Plantilla": lst("plantilla", "Plantilla")[:1], "Palanca": lst("palanca", "Palanca"),
            "Soporte": lst("soporte", "Soporte")[:1],
            "Etiquetas del cliente": [x for x in (res.get("etiquetas_cliente") or []) if x in propias][:3]}


def texto(props, k):
    v = na.plain(props.get(k))
    return v if isinstance(v, str) else (", ".join(v) if v else "")


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(description="Gemini ve los vídeos y los etiqueta.")
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true", help="Analiza e imprime; no escribe en Notion.")
    ap.add_argument("--sin-ig", action="store_true", help="No usar Instagram.")
    ap.add_argument("--fila", help="Solo esta fila de rendimiento (page id).")
    ap.add_argument("--parte", help="k/n: solo la parte k de n (para repartir una pasada larga en varios procesos).")
    ap.add_argument("--con-palanca", help="Solo filas que lleven esta palanca (p. ej. Emoción, para reetiquetarlas).")
    a = ap.parse_args()
    try:
        tok, cli = na.token(), cliente_gemini()
    except RuntimeError as e:
        print(e)
        return 2
    cfg = na.load_config()
    c = cfg["clientes"].get(a.cliente) or cfg.get("exclientes", {}).get(a.cliente)
    if not c or not c.get("rendimiento_db"):
        print(f"{a.cliente}: sin rendimiento_db en config/notion-bases.json")
        return 1
    etq, listas, definiciones = cfg_etiquetas()
    en_contenido = etq.get("etiquetas_viven_en", {}).get(a.cliente) == "contenido"
    if a.dry_run:
        esq_rend = na._request("GET", f"/databases/{c['rendimiento_db']}", tok)["properties"]
        esq_cont = na._request("GET", f"/databases/{c['database_id']}", tok)["properties"] if en_contenido else {}
    else:
        esq_rend = asegurar_columnas(c["rendimiento_db"], tok, multi=True)
        esq_cont = asegurar_columnas(c["database_id"], tok, multi=False) if en_contenido else {}

    contenido = {}
    if en_contenido:
        for pg in na.query(c["database_id"], tok):
            contenido[pg["id"].replace("-", "")] = pg
    hoy = datetime.date.today()
    cola = []
    for pg in na.query(c["rendimiento_db"], tok):
        p = pg["properties"]
        if a.fila and pg["id"].replace("-", "") != a.fila.replace("-", ""):
            continue
        fecha = (na.plain(p.get("Fecha")) or "")[:10]
        if not fecha or texto(p, "Estado") == "Pendiente" or datetime.date.fromisoformat(fecha) > hoy:
            continue
        ficha = None
        if en_contenido:
            rel = (p.get("Pieza de producción") or {}).get("relation") or []
            ficha = contenido.get(rel[0]["id"].replace("-", "")) if rel else None
        fp = (ficha or pg)["properties"]
        fuente = texto(fp, "Etiquetado por")
        if fuente.startswith(("Gerard", "Gemini")):
            continue
        if a.con_palanca and a.con_palanca not in (na.plain(fp.get("Palanca")) or []):
            continue
        cola.append((pg, ficha))
    # Primero lo que más pesa en las conclusiones: más vistas.
    cola.sort(key=lambda t: -(sum((t[0]["properties"].get(f"{r} Vistas") or {}).get("number") or 0
                                  for r in ("IG", "TT", "YT"))))
    if a.parte:
        k, n = (int(x) for x in a.parte.split("/"))
        cola = cola[k - 1::n]
    cola = cola[:a.max]
    print(f"{a.cliente}: {len(cola)} vídeos a ver · coste orientativo ≈ {len(cola) * USD_POR_VIDEO:.2f} USD")

    hechos = 0
    propias = (etq.get("etiquetas_cliente", {}).get(a.cliente) or {}).get("opciones", [])
    # La columna propia del cliente se crea aquí si falta: sin ella Gemini las calculaba y se
    # perdían (pasó con Jesús y NewMos el 02/10/2026; se recuperaron del log).
    if propias and not a.dry_run and "Etiquetas del cliente" not in esq_rend:
        na._request("PATCH", f"/databases/{c['rendimiento_db']}", tok, {"properties": {
            "Etiquetas del cliente": {"multi_select": {"options": [{"name": o} for o in propias]}}}})
        esq_rend = na._request("GET", f"/databases/{c['rendimiento_db']}", tok)["properties"]
    for pg, ficha in cola:
        p = pg["properties"]
        titulo = texto(p, "Pieza")[:70]
        copy = texto(p, "Copy") or titulo
        titulo_ficha = texto(ficha["properties"], "Idea") if ficha else ""
        fuentes = []
        if texto(p, "TT URL") or texto(p, "TikTok URL"):
            fuentes.append(("TikTok", texto(p, "TT URL") or texto(p, "TikTok URL")))
        if ficha and texto(ficha["properties"], "Vídeo final"):
            fuentes.append(("Drive", texto(ficha["properties"], "Vídeo final")))
        fuentes.append(("Disco", titulo_ficha or titulo))
        if texto(p, "IG URL") and not a.sin_ig:
            fuentes.append(("Instagram", texto(p, "IG URL")))
        res = origen = modelo = None
        for nombre, ref in fuentes:
            tmp = tempfile.mkdtemp(prefix="ver_video_")
            try:
                if nombre == "TikTok":
                    ruta = bajar_ytdlp(ref, tmp)
                elif nombre == "Drive":
                    ruta = bajar_drive(ref, tmp)
                elif nombre == "Disco":
                    ruta = buscar_disco(a.cliente, ref, (na.plain(p.get("Fecha")) or "")[:10])
                else:
                    time.sleep(PAUSA_IG)
                    ruta = bajar_ytdlp(ref, tmp, ig=True)
                if not ruta or not os.path.exists(ruta):
                    continue
                r, modelo = analizar(cli, ruta, prompt_para(listas, c["label"], copy, propias, definiciones))
                if r.get("coincide") is False:
                    print(f"   · {nombre}: el vídeo no casa con el copy, pruebo otra fuente")
                    continue
                res, origen = r, (nombre if nombre != "Disco" else "Disco: " + os.path.basename(ruta))
                break
            except CuotaAgotada:
                print("\n⛔ Cuota de Gemini agotada (plan gratuito: 20 vídeos/día por modelo). "
                      "Paro aquí; lo hecho está guardado y la próxima pasada sigue por donde quedó.")
                print(f"\n{hechos}/{len(cola)} vídeos vistos.")
                return 3
            except Exception as e:
                print(f"   · {nombre}: {str(e)[:120]}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)   # nada descargado se queda en el Mac
        fuente = ETQ_FUENTE
        if not res:
            # Plan B (02/10/2026): sin vídeo, Gemini etiqueta desde el COPY y queda marcado como tal,
            # para que el panel lo distinga. Una fila ya deducida no se vuelve a pagar.
            ya = texto((ficha or pg)["properties"], "Etiquetado por") or texto(p, "Etiquetado por")
            if ya.startswith("Deducido") or len(copy) < 25:
                print(f"✗ {titulo}: no encontré el vídeo en ninguna fuente")
                continue
            try:
                res, modelo = analizar(cli, None, "NO TIENES EL VÍDEO: solo el copy con el que se publicó. "
                                       "Etiqueta únicamente lo que el copy deje claro y deja vacío lo demás; "
                                       "pon \"coincide\": true.\n\n" + prompt_para(listas, c["label"], copy, propias, definiciones))
            except CuotaAgotada:
                print("\n⛔ Cuota de Gemini agotada. Paro aquí.")
                return 3
            except Exception as e:
                print(f"✗ {titulo}: sin vídeo y el copy tampoco se pudo leer ({str(e)[:80]})")
                continue
            origen, fuente = "Copy (sin vídeo)", "Deducido del copy"
        etiquetas = limpiar(res, listas, propias)
        sugerido = "" if etiquetas["Formato"] else (res.get("formato_sugerido") or "").strip()
        porque = (f"{res.get('por_que', '')} · Gancho: {res.get('gancho', '')}"
                  + (f" · Formato sugerido (no está en la lista): {sugerido}" if sugerido else "")
                  + f" · ({origen}, {modelo}, confianza {res.get('confianza')})")
        print(f"✓ {titulo}\n   {origen} · " + " · ".join(f"{k}: {', '.join(v)}" for k, v in etiquetas.items() if v)
              + (f" · formato sugerido: {sugerido}" if sugerido else "")
              + f"\n   {res.get('por_que', '')}")
        hechos += 1
        if a.dry_run:
            continue
        destino, esquema = (ficha, esq_cont) if (en_contenido and ficha) else (pg, esq_rend)
        actual = destino["properties"]
        props = {}
        for campo in CAMPOS:
            # El Soporte lo sabe Metricool (Reel/Carrusel/Imagen), no Gemini: en la fila de
            # rendimiento no se pisa nunca (04/10/2026, pisó carruseles de NewMos como Reel).
            if campo == "Soporte" and destino is pg:
                continue
            vacio = not na.plain(actual.get(campo))
            pisar = not en_contenido or vacio
            if en_contenido and campo == "Plantilla" and not vacio:
                pisar = False
            v = valor_prop(esquema, campo, etiquetas[campo])
            if v and pisar:
                props[campo] = v
        if "Etiquetado por" in esquema:
            props["Etiquetado por"] = {"select": {"name": fuente}}
        if props:
            na.update_props(destino["id"], tok, props)
        fila = {COL_PORQUE: na.prop_text(porque[:1900])} if COL_PORQUE in esq_rend else {}
        if (etiquetas["Etiquetas del cliente"] and "Etiquetas del cliente" in esq_rend
                and not na.plain(p.get("Etiquetas del cliente"))):
            fila["Etiquetas del cliente"] = na.prop_multi(etiquetas["Etiquetas del cliente"])
        if fila:
            na.update_props(pg["id"], tok, fila)
    print(f"\n{hechos}/{len(cola)} vídeos vistos{' (dry-run: nada escrito)' if a.dry_run else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
