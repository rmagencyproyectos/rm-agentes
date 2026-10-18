#!/usr/bin/env python3
"""Vuelca a Notion el rendimiento de cada vídeo de Xavi que hay en el planner de Metricool.

Destino: base «📊 Rendimiento de vídeos (Metricool)» dentro de la página Xavi Colomina.
Una fila por vídeo. Qué hace en cada pasada:

- Lee el planner (publicados + pendientes + borradores) y las analíticas de Reels de IG,
  TikTok y YouTube, y las cruza por el ID de cada red.
- Los Shorts del reto se subieron a YouTube a mano, fuera del planner: se cruzan por
  fecha y hora (±15 min). Lo publicado fuera del planner entra como «Fuera del planner».
- Actualiza SOLO lo automático: métricas, estado, variables sacadas del copy (hashtags,
  CTA, longitud), hora/día y los seguidores ganados ese día en la cuenta.
- NO toca la clasificación hecha a mano (Línea, Tema, Tipo de gancho, Tono, Rodaje (antes «Formato», renombrada el 02/10/2026),
  Pieza de producción) ni unas Notas escritas a mano.
- Los vídeos nuevos se crean sin clasificar y se listan al final: hay que clasificarlos.

Seguidores: Metricool no da seguidores por vídeo (Instagram no lo expone para Reels).
Se guarda el total diario de la cuenta y cuántos vídeos salieron ese día, para no
atribuirle a un vídeo lo que trajeron varios.

Uso:  python3 analitica/metricool_a_notion.py            (escribe en Notion)
      python3 analitica/metricool_a_notion.py --dry-run  (solo enseña qué haría)
"""
import datetime as dt
import json
import re
import statistics
import sys
import urllib.parse
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, HUB + "/infra/notion")
import notion_api as na  # noqa: E402

BLOG = 6276334                              # marca Xavi Colomina en Metricool
DB = "2cb8b6309dce4e1bae929f279d82ec47"     # 📊 Rendimiento de vídeos (Metricool)
RETO_PAGE = "3b2496ca6d5180da9ca6e7fea4fc22cc"  # «SERIE Aprenent esquerra» en Contenido
DESDE = "2026-08-01"
API = "https://app.metricool.com/api"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def env():
    e = {}
    for line in open(HUB + "/infra/.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            e[k] = v
    return e


E = env()
TOK, UID = E["METRICOOL_API_TOKEN"], E["METRICOOL_USER_ID"]


def mc(path, **params):
    params.update(blogId=BLOG, userId=UID)
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"X-Mc-Auth": TOK, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def serie_diaria(network, metric):
    """{fecha: valor} de un timeline de cuenta."""
    hoy = dt.date.today().isoformat()
    d = mc("/v2/analytics/timelines", **{"from": DESDE + "T00:00:00", "to": hoy + "T23:59:59",
                                         "network": network, "metric": metric, "subject": "account"})
    vals = d["data"][0]["values"] if d.get("data") else []
    return {v["dateTime"][:10]: v["value"] for v in vals}


def descargar():
    hoy = dt.date.today().isoformat()
    rango = {"from": DESDE + "T00:00:00", "to": hoy + "T23:59:59"}
    fin = (dt.date.today() + dt.timedelta(days=120)).isoformat()
    return {
        "planner": mc("/v2/scheduler/posts", start=DESDE + "T00:00:00", end=fin + "T23:59:59",
                      extendedRange="true")["data"],
        "ig": mc("/v2/analytics/reels/instagram", **rango)["data"],
        "tt": mc("/v2/analytics/posts/tiktok", **rango)["data"],
        "yt": mc("/v2/analytics/posts/youtube", **rango)["data"],
        "ig_seg": serie_diaria("instagram", "delta_followers"),
        "ig_perfil": serie_diaria("instagram", "profile_views"),
        "tt_seg": serie_diaria("tiktok", "followers_delta_count"),
    }


def t(s):
    return dt.datetime.fromisoformat(s[:19])


def reel_code(u):
    m = re.search(r"/reel/([^/?]+)", u or "")
    return m.group(1) if m else None


def cruzar(d):
    ig = {reel_code(r["url"]): r for r in d["ig"]}
    tt = {r["videoId"]: r for r in d["tt"]}
    yt = {r["videoId"]: r for r in d["yt"]}
    usados = set()
    filas = []
    for p in d["planner"]:
        igd = p.get("instagramData") or {}
        if igd.get("type") == "POST":          # carruseles/imágenes: no son vídeo
            continue
        f = {"mid": str(p["id"]), "fecha": p["publicationDate"]["dateTime"], "texto": p.get("text") or "",
             "yt_title": (p.get("youtubeData") or {}).get("title", ""), "ig_type": igd.get("type", ""),
             "draft": p.get("draft"), "redes": {}, "fuera": False}
        for pr in p["providers"]:
            red, pid = pr["network"], str(pr.get("id", ""))
            f["redes"][red] = {"status": pr["status"], "url": pr.get("publicUrl", "")}
            if red == "instagram" and reel_code(pid) in ig:
                f["ig"] = ig[reel_code(pid)]; usados.add(("ig", reel_code(pid)))
            elif red == "tiktok" and pid in tt:
                f["tt"] = tt[pid]; usados.add(("tt", pid))
            elif red == "youtube" and pid in yt:
                f["yt"] = yt[pid]; usados.add(("yt", pid))
        filas.append(f)
    # Shorts subidos a mano a YouTube: solo para posts que salen en IG+TT y no tienen YT
    libres = {k: v for k, v in yt.items() if ("yt", k) not in usados and v["videoType"] == "SHORT"}
    for f in filas:
        if "yt" in f or "youtube" in f["redes"] or "tiktok" not in f["redes"]:
            continue
        for k, v in list(libres.items()):
            if abs((t(v["publishedAt"]["dateTime"]) - t(f["fecha"])).total_seconds()) <= 900:
                f["yt"] = v; usados.add(("yt", k)); del libres[k]; break
    # Lo publicado fuera del planner
    for k, v in yt.items():
        if ("yt", k) not in usados:
            filas.append({"mid": None, "fecha": v["publishedAt"]["dateTime"], "texto": v.get("description", ""),
                          "yt_title": v["title"], "ig_type": "", "draft": False, "fuera": True, "yt": v,
                          "redes": {"youtube": {"status": "PUBLISHED", "url": ""}}})
    for k, v in ig.items():
        if ("ig", k) not in usados:
            filas.append({"mid": None, "fecha": v["publishedAt"]["dateTime"], "texto": v.get("content", ""),
                          "yt_title": "", "ig_type": "REEL", "draft": False, "fuera": True, "ig": v,
                          "redes": {"instagram": {"status": "PUBLISHED", "url": v["url"]}}})
    filas.sort(key=lambda f: f["fecha"])
    return filas


def cta(texto):
    x = texto.lower()
    if "dm" in re.findall(r"\bdm\b", x) or "diagnóstico" in x:
        return "DM diagnóstico"
    if "youtube" in x:
        return "Ver en YouTube"
    if re.search(r"s[ií]gue(me)?\b|suscr[ií]bete|ponle soluci[oó]n|no le sigues", x):
        return "Seguir la cuenta"
    if re.search(r"coment|d[ée]jame|dime en|sacáis vosotros", x):
        return "Comentar"
    return "Sin CTA"


def franja(h):
    return "Mañana (9-12)" if h < 12 else "Mediodía (12-15)" if h < 15 else "Tarde (15-20)" if h < 20 else "Noche (20-23)"


def rt(s):
    s = s or ""
    return [{"type": "text", "text": {"content": s[i:i + 1900]}} for i in range(0, min(len(s), 5700), 1900)]


def props_auto(f, d, publicados_por_dia):
    """Propiedades que el script mantiene. Lo manual no aparece aquí."""
    ig, tt, yt = f.get("ig"), f.get("tt"), f.get("yt")
    estados = [v["status"] for v in f["redes"].values()]
    estado = "Publicado" if "PUBLISHED" in estados else ("Borrador" if f["draft"] else "Pendiente")
    fecha = t(f["fecha"])
    dia = fecha.date().isoformat()
    tags = sorted(set(re.findall(r"#(\w+)", f["texto"])), key=str.lower)
    P = {
        "Estado": {"select": {"name": estado}},
        "Origen": {"select": {"name": "Fuera del planner" if f["fuera"] else "Planner Metricool"}},
        "Fecha": {"date": {"start": fecha.strftime("%Y-%m-%dT%H:%M:00") + "+02:00"}},
        "Hora": {"rich_text": rt(fecha.strftime("%H:%M"))},
        "Día de la semana": {"select": {"name": DIAS[fecha.weekday()]}},
        "Franja horaria": {"select": {"name": franja(fecha.hour)}},
        "Copy": {"rich_text": rt(f["texto"])},
        "Hashtags": {"multi_select": [{"name": h[:90]} for h in tags[:30]]},
        "Nº hashtags": {"number": len(tags)},
        "Longitud copy (car.)": {"number": len(f["texto"])},
        "CTA": {"select": {"name": cta(f["texto"])}},
    }
    if f["yt_title"]:
        P["Título YT"] = {"rich_text": rt(f["yt_title"])}
    if f["mid"]:
        P["Metricool ID"] = {"rich_text": rt(f["mid"])}
    # Gerard (10/10/2026): los largos de YouTube van en su pestaña («🎬 Largos YouTube»,
    # filtro Soporte = «Vídeo largo»). Un vídeo de YouTube que no es short es un largo.
    if yt and yt.get("videoType") and yt["videoType"] != "SHORT":
        P["Soporte"] = {"select": {"name": "Vídeo largo"}}
        P["Serie"] = {"select": {"name": "Vídeo largo YouTube"}}
    if f["ig_type"] == "TRIAL_REEL":
        P["Distribución IG"] = {"select": {"name": "Trial reel"}}
    elif f["ig_type"] == "REEL" or ig:
        P["Distribución IG"] = {"select": {"name": "Reel"}}
    else:
        P["Distribución IG"] = {"select": {"name": "Sin IG"}}
    dur = (ig or {}).get("durationSeconds") or (tt or {}).get("duration") or (yt or {}).get("durationSeconds")
    if dur:
        P["Duración (s)"] = {"number": round(dur)}
    r = f["redes"]
    if r.get("instagram", {}).get("url") or ig:
        P["IG URL"] = {"url": (ig or {}).get("url") or r["instagram"]["url"]}
    if r.get("tiktok", {}).get("url") or tt:
        P["TikTok URL"] = {"url": ((tt or {}).get("shareUrl") or "").split("?")[0] or r["tiktok"]["url"]}
    if yt:
        base = "https://www.youtube.com/shorts/" if yt["videoType"] == "SHORT" else "https://www.youtube.com/watch?v="
        P["YouTube URL"] = {"url": base + yt["videoId"]}
    elif r.get("youtube", {}).get("url"):
        P["YouTube URL"] = {"url": r["youtube"]["url"]}
    n = lambda v: {"number": round(v, 2) if isinstance(v, float) else v}  # noqa: E731
    if ig:
        P.update({"IG Vistas": n(ig["views"]), "IG Alcance": n(ig["reach"]), "IG Likes": n(ig["likes"]),
                  "IG Comentarios": n(ig["comments"]), "IG Guardados": n(ig["saved"]),
                  "IG Compartidos": n(ig["shares"]), "IG Interacciones": n(ig["interactions"]),
                  "IG Engagement %": n(round(ig.get("engagement") or 0, 2)),
                  "IG Tiempo medio visto (s)": n(round(ig.get("averageWatchTime") or 0, 1)),
                  "IG Tiempo total visto (min)": n(round((ig.get("videoViewTotalTime") or 0) / 60, 1)),
                  "IG Skip rate %": n(round(ig.get("reelsSkipRate") or 0, 1))})
    if tt:
        src = tt.get("impressionSources") or {}
        P.update({"TT Vistas": n(tt["viewCount"]), "TT Likes": n(tt["likeCount"]),
                  "TT Comentarios": n(tt["commentCount"]), "TT Compartidos": n(tt["shareCount"]),
                  "TT Tiempo medio visto (s)": n(round(tt.get("averageTimeWatched") or 0, 1)),
                  "TT % visto completo": n(round((tt.get("fullVideoWatchedRate") or 0) * 100, 1)),
                  "TT % desde For You": n(src.get("forYou") or 0), "TT % desde perfil": n(src.get("personalProfile") or 0),
                  "TT % desde seguidores": n(src.get("follow") or 0), "TT % desde búsqueda": n(src.get("search") or 0)})
        if tt["viewCount"]:
            P["TT Engagement %"] = n(round(engagement("tt", tt), 2))
    if yt:
        P.update({"YT Vistas": n(int(yt["views"])), "YT Vistas comprometidas": n(int(yt.get("engagedViews") or 0)),
                  "YT Duración media vista (s)": n(round(yt.get("averageViewDuration") or 0, 1)),
                  "YT Likes": n(int(yt.get("likes") or 0)), "YT Comentarios": n(int(yt.get("comments") or 0)),
                  "YT Compartidos": n(int(yt.get("shares") or 0))})
        if yt["views"]:
            P["YT Engagement %"] = n(round(engagement("yt", yt), 2))
    if estado == "Publicado":
        P["Vídeos publicados ese día"] = {"number": publicados_por_dia.get(dia, 1)}
        for campo, serie in [("IG Seguidores ganados ese día (cuenta)", "ig_seg"),
                             ("IG Visitas al perfil ese día (cuenta)", "ig_perfil"),
                             ("TT Seguidores ganados ese día (cuenta)", "tt_seg")]:
            if dia in d[serie]:
                P[campo] = {"number": d[serie][dia]}
    if ig or tt or yt:
        P["Métricas a fecha"] = {"date": {"start": dt.date.today().isoformat()}}
    return P, estado


# ── Veredicto por red (criterio de Gerard, 25/09/2026) ────────────────────────────────────
# Cada red se juzga por separado con TRES métricas: visualizaciones, retención y engagement.
# Comparación GENÉRICA: contra todos los vídeos publicados en esa red (≥48 h), no contra su
# grupo. Cada métrica cae en su tercio: alto (≥ p67), medio o bajo (< p34).
#   ✅ Apto        visualizaciones altas sin retención ni engagement bajos,
#                  visualizaciones y retención altas (aunque el engagement sea bajo),
#                  o visualizaciones medias con retención Y engagement altos.
#   🔍 Revisar     pocas visualizaciones pero retención y engagement al menos medios y uno alto:
#                  el contenido engancha y algo ha fallado en la distribución. Se revisa a mano.
#   ❌ No apto     pocas visualizaciones y retención o engagement bajos.
#   🟡 Regular     el resto (p. ej. muchas visualizaciones que no retienen).
# La nota 0-100 pondera 40 % retención, 35 % visualizaciones y 25 % engagement.
# «Vs su grupo» repite el cálculo solo dentro de su grupo: es la lectura secundaria.
PESOS = {"views": 0.35, "ret": 0.40, "eng": 0.25}
RED_ES = {"ig": "IG", "tt": "TT", "yt": "YT"}
GRUPO_ES = {"principal": "serie principal", "trial": "trial reels del reto", "reto": "reto",
            "largo": "vídeos largos"}


def engagement(red, x):
    if red == "ig":
        return x.get("engagement") or 0          # Metricool: interacciones / alcance × 100
    if red == "tt":
        v = x.get("viewCount") or 0
        return (x.get("likeCount", 0) + x.get("commentCount", 0) + x.get("shareCount", 0)) / v * 100 if v else 0
    v = x.get("views") or 0
    return ((x.get("likes") or 0) + (x.get("comments") or 0) + (x.get("shares") or 0)) / v * 100 if v else 0


def metricas(f, red):
    """(views, retención %, engagement %) de un vídeo en una red, o None si no hay datos."""
    x = f.get(red)
    if not x:
        return None
    dur = (f.get("ig") or {}).get("durationSeconds") or (f.get("tt") or {}).get("duration") \
        or (f.get("yt") or {}).get("durationSeconds")
    visto = {"ig": x.get("averageWatchTime"), "tt": x.get("averageTimeWatched"),
             "yt": x.get("averageViewDuration")}[red]
    views = {"ig": x.get("views"), "tt": x.get("viewCount"), "yt": x.get("views")}[red] or 0
    if not dur or visto is None:
        return None
    return views, visto / dur * 100, engagement(red, x)


def grupo_de(f, red):
    yt = f.get("yt") or {}
    if red == "yt" and yt.get("videoType") == "VIDEO":
        return "largo"
    if f["ig_type"] == "TRIAL_REEL" or (f["fuera"] and yt.get("videoType") == "SHORT"):
        return "trial" if red == "ig" else "reto"
    return "principal"


def percentil(x, pool):
    return (sum(1 for v in pool if v < x) + 0.5 * sum(1 for v in pool if v == x)) / len(pool)


def nivel(p):
    return "alto" if p >= 0.67 else "bajo" if p < 0.34 else "medio"


def clasificar(nv, nr, ne):
    if nv == "alto" and "bajo" not in (nr, ne):
        return "✅ Apto"
    # Con mucho alcance el engagement en % cae solo (el globo en YT: 91 likes / 11.276 = 0,8 %).
    # La retención es lo que más pesa, así que si retiene alto, el engagement bajo no lo tumba.
    if nv == nr == "alto":
        return "✅ Apto"
    if nv == "medio" and nr == ne == "alto":
        return "✅ Apto"
    if nv == "bajo" and "bajo" not in (nr, ne) and "alto" in (nr, ne):
        return "🔍 Revisar"
    if nv == "bajo":
        return "❌ No apto"
    return "🟡 Regular"


def resumen(sig, v, nv):
    """«IG 🔍 · views bajas · retención alta · engagement alto» — para leerlo de un vistazo."""
    fem = {"alto": "altas", "medio": "medias", "bajo": "bajas"}
    f1 = {"alto": "alta", "medio": "media", "bajo": "baja"}
    return f"{sig} {v.split()[0]} · views {fem[nv[0]]} · retención {f1[nv[1]]} · engagement {nv[2]}"


def evaluar(filas):
    """{id(fila): propiedades de veredicto} para las tres redes."""
    corte = dt.datetime.now() - dt.timedelta(hours=48)
    maduro = lambda f: t(f["fecha"]) <= corte  # noqa: E731
    datos = {red: {id(f): metricas(f, red) for f in filas if metricas(f, red)} for red in RED_ES}
    out = {}
    for f in filas:
        P, grupo_txt, res_txt = {}, [], []
        for red, sig in RED_ES.items():
            m3 = datos[red].get(id(f))
            if not m3:
                continue
            if not maduro(f):
                P[f"{sig} Veredicto"] = {"select": {"name": "⏳ Muy reciente"}}
                continue
            pools = [ff for ff in filas if id(ff) in datos[red] and maduro(ff)]
            pg = [ff for ff in pools if grupo_de(ff, red) == grupo_de(f, red)]
            res = {}
            for nombre, pool in (("gen", pools), ("grp", pg)):
                if len(pool) < 3:
                    continue
                ps = [percentil(m3[i], [datos[red][id(ff)][i] for ff in pool]) for i in range(3)]
                res[nombre] = (ps, [nivel(p) for p in ps])
            ps, nv = res["gen"]
            nota = round(100 * (PESOS["views"] * ps[0] + PESOS["ret"] * ps[1] + PESOS["eng"] * ps[2]))
            v = clasificar(*nv)
            P[f"{sig} Veredicto"] = {"select": {"name": v}}
            P[f"{sig} Nota"] = {"number": nota}
            lectura = (f"Visualizaciones {int(m3[0]):,} ({nv[0]}) · Retención {m3[1]:.0f}% ({nv[1]}) · "
                       f"Engagement {m3[2]:.1f}% ({nv[2]})").replace(",", ".")
            if v == "🔍 Revisar":
                lectura += " → engancha pero no se ha distribuido: revisar qué ha fallado."
            elif v == "🟡 Regular" and nv[0] == "alto":
                lectura += " → llega a mucha gente pero no engancha."
            P[f"{sig} Lectura"] = {"rich_text": rt(lectura)}
            res_txt.append(resumen(sig, v, nv))
            if "grp" in res:
                grupo_txt.append(f"{sig} {clasificar(*res['grp'][1])} ({GRUPO_ES[grupo_de(f, red)]})")
        if grupo_txt:
            P["Vs su grupo"] = {"rich_text": rt(" · ".join(grupo_txt))}
        if res_txt:
            P["Qué ha pasado (auto)"] = {"rich_text": rt("\n".join(res_txt))}
        out[id(f)] = P
    return out


def plano(prop):
    if not prop:
        return ""
    tipo = prop["type"]
    v = prop[tipo]
    if tipo in ("title", "rich_text"):
        return "".join(x["plain_text"] for x in v)
    if tipo == "select":
        return v["name"] if v else ""
    if tipo == "url":
        return v or ""
    if tipo == "date":
        return (v or {}).get("start", "")
    return v


def main():
    seco = "--dry-run" in sys.argv
    d = descargar()
    filas = cruzar(d)
    pub_dia = {}
    for f in filas:
        if any(v["status"] == "PUBLISHED" for v in f["redes"].values()):
            k = f["fecha"][:10]; pub_dia[k] = pub_dia.get(k, 0) + 1
    ver = evaluar(filas)

    tok = na.token()
    existentes = na.query(DB, tok)
    por_mid, por_url, por_fecha = {}, {}, {}
    for pg in existentes:
        pr = pg["properties"]
        if plano(pr.get("Metricool ID")):
            por_mid[plano(pr["Metricool ID"])] = pg
        for c in ("IG URL", "YouTube URL", "TikTok URL"):
            if plano(pr.get(c)):
                por_url[plano(pr[c]).rstrip("/")] = pg
        por_fecha[plano(pr.get("Fecha"))[:16]] = pg

    nuevas, act = [], 0
    for f in filas:
        P, estado = props_auto(f, d, pub_dia)
        pg = por_mid.get(f["mid"]) if f["mid"] else None
        if not pg:
            for c in ("IG URL", "YouTube URL", "TikTok URL"):
                u = (P.get(c) or {}).get("url")
                if u and u.rstrip("/") in por_url:
                    pg = por_url[u.rstrip("/")]; break
        P.update(ver.get(id(f), {}))
        if pg:
            # Las notas automáticas del criterio antiguo (solo visualizaciones) ya no valen.
            if plano(pg["properties"].get("Notas")).startswith("IG+TT ="):
                P["Notas"] = {"rich_text": []}
            if not seco:
                na.update_props(pg["id"], tok, P)
            act += 1
        else:
            lineas = [x for x in f["texto"].split("\n") if x.strip()]
            titulo = f["yt_title"] if (f["fuera"] and not f.get("ig")) else (lineas[0] if lineas else f["yt_title"])
            P["Pieza"] = {"title": rt(titulo[:120])}
            if f["ig_type"] == "TRIAL_REEL":
                P["Serie"] = {"select": {"name": "Reto mano izquierda"}}
                P["Línea"] = {"select": {"name": "Reto mano izquierda"}}
                P["Pieza de producción"] = {"relation": [{"id": RETO_PAGE}]}
            if not seco:
                na.create_page(DB, tok, P)
            nuevas.append(f"{f['fecha'][:16]}  {titulo[:70]}")

    print(f"{'[simulación] ' if seco else ''}Actualizadas: {act} · Nuevas: {len(nuevas)}")
    for sig in RED_ES.values():
        c = {}
        for P in ver.values():
            v = (P.get(f"{sig} Veredicto") or {}).get("select", {}).get("name")
            if v:
                c[v] = c.get(v, 0) + 1
        print(f"{sig}:", dict(sorted(c.items())))
    if nuevas:
        print("\nVídeos NUEVOS sin clasificar (rellenar Línea, Tema, Tipo de gancho, Tono):")
        for x in nuevas:
            print("  -", x)


if __name__ == "__main__":
    main()
