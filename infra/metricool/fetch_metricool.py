#!/usr/bin/env python3
"""Fetcher de métricas de Metricool para el Estratega (Sun).

Descarga el contenido reciente de cada cliente del roster v1 en TODAS sus fuentes:
- **Reels de Instagram** (`/v2/analytics/reels/instagram`) — el grueso del vídeo.
- **Feed de Instagram** (`/v2/analytics/posts/instagram`) — imágenes y carruseles.
- **TikTok** (`/v2/analytics/posts/tiktok`).
Los normaliza a un esquema común y escribe, por cliente, un resumen legible (.md) +
estructurado (.json) en `memoria/metricas/`: rendimiento por red y formato + top posts.

Config: token + userId en `infra/.env` (METRICOOL_API_TOKEN, METRICOOL_USER_ID).
Mapeo cliente→marca en `config/metricool-marcas.json`. Ventana: METRICOOL_DAYS (def. 180).
"""
import datetime
import json
import os
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
API = "https://app.metricool.com/api"
DAYS = int(os.environ.get("METRICOOL_DAYS", "180"))

TYPE_ES = {
    "FEED_IMAGE": "Imagen", "FEED_CAROUSEL_ALBUM": "Carrusel", "FEED_VIDEO": "Vídeo",
    "REELS": "Reel", "REEL": "Reel", "STORY": "Story",
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


def api_get(path, tok):
    r = urllib.request.Request(API + path, headers={"X-Mc-Auth": tok, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=40) as resp:
        return json.loads(resp.read().decode())


def n(d, *keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            return v
    return 0


def fecha_de(p):
    pa = p.get("publishedAt")
    if isinstance(pa, dict):
        return (pa.get("dateTime") or "")[:10]
    ct = p.get("createTime")
    if isinstance(ct, dict):
        return (ct.get("dateTime") or "")[:10]
    if isinstance(ct, str):
        return ct[:10]
    if isinstance(ct, (int, float)):
        try:
            return datetime.datetime.fromtimestamp(ct / (1000 if ct > 1e12 else 1)).strftime("%Y-%m-%d")
        except Exception:
            return ""
    return ""


def norm_ig_feed(p):
    return {"red": "Instagram", "formato": TYPE_ES.get(p.get("type"), "Feed"),
            "fecha": fecha_de(p), "vistas": n(p, "views"), "alcance": n(p, "reach"),
            "interacciones": n(p, "interactions"), "guardados": n(p, "saved"),
            "likes": n(p, "likes"), "engagement": round(n(p, "engagement"), 2),
            "url": p.get("url", ""), "texto": (p.get("content") or "").split("\n")[0][:90],
            # `texto` es el recorte que sale en el .md (una línea); `copy` es el copy ENTERO,
            # que necesitan los análisis por pieza (infra/notion/rendimiento.py).
            "copy": (p.get("content") or "")[:1800]}


def norm_ig_reel(p):
    return {"red": "Instagram", "formato": "Reel", "fecha": fecha_de(p),
            "vistas": n(p, "views"), "alcance": n(p, "reach"),
            "interacciones": n(p, "interactions"), "guardados": n(p, "saved"),
            "likes": n(p, "likes"), "engagement": round(n(p, "engagement"), 2),
            "url": p.get("url", ""), "texto": (p.get("content") or "").split("\n")[0][:90],
            # `texto` es el recorte que sale en el .md (una línea); `copy` es el copy ENTERO,
            # que necesitan los análisis por pieza (infra/notion/rendimiento.py).
            "copy": (p.get("content") or "")[:1800]}


def norm_tiktok(p):
    inter = n(p, "interactions") or (n(p, "likeCount") + n(p, "commentCount") + n(p, "shareCount"))
    return {"red": "TikTok", "formato": "Vídeo", "fecha": fecha_de(p),
            "vistas": n(p, "viewCount", "views"), "alcance": n(p, "reach"),
            "interacciones": inter, "guardados": n(p, "saved"),
            "likes": n(p, "likeCount", "likes"), "engagement": round(n(p, "engagement"), 2),
            "url": p.get("shareUrl", "") or p.get("url", ""),
            "texto": (p.get("videoDescription") or p.get("title") or "").split("\n")[0][:90],
            "copy": (p.get("videoDescription") or p.get("title") or "")[:1800]}


def fetch_all(blog, uid, tok):
    now = datetime.datetime.now()
    fr = (now - datetime.timedelta(days=DAYS)).strftime("%Y-%m-%dT00:00:00")
    to = now.strftime("%Y-%m-%dT23:59:59")
    q = f"from={fr}&to={to}&blogId={blog}&userId={uid}"
    rows = []
    sources = [("/v2/analytics/reels/instagram?" + q, norm_ig_reel),
               ("/v2/analytics/posts/instagram?" + q, norm_ig_feed),
               ("/v2/analytics/posts/tiktok?" + q, norm_tiktok)]
    fallos = []
    for path, fn in sources:
        try:
            data = api_get(path, tok)
            for p in (data.get("data", []) if isinstance(data, dict) else []):
                rows.append(fn(p))
        except Exception as e:
            fallos.append(f"{path.split('?')[0]}: {e}")
    # Si fallan TODAS las fuentes es un problema de red/credenciales, no "este cliente no
    # tiene contenido". Hay que distinguirlo: si no, se sobrescriben las métricas buenas
    # con ficheros vacíos y se pierde el histórico.
    if fallos and len(fallos) == len(sources):
        raise RuntimeError("todas las fuentes fallaron :: " + " | ".join(fallos))
    return rows


TOP_POR_RED = 10   # publicaciones que se guardan por red (antes se guardaban TODAS)


def avg(xs):
    return round(sum(xs) / len(xs)) if xs else 0


def summarize(cli, label, rows):
    # Agrupar por red+formato
    groups = {}
    for r in rows:
        key = f"{r['red']} · {r['formato']}"
        g = groups.setdefault(key, [])
        g.append(r)
    por_grupo = {}
    for key, g in groups.items():
        por_grupo[key] = {
            "n": len(g),
            "vistas_medias": avg([r["vistas"] for r in g]),
            "alcance_medio": avg([r["alcance"] for r in g]),
            "interacciones_medias": avg([r["interacciones"] for r in g]),
            "guardados_medios": round(sum(r["guardados"] for r in g) / len(g), 1),
        }
    por_grupo = dict(sorted(por_grupo.items(), key=lambda kv: kv[1]["vistas_medias"], reverse=True))
    # Top posts por impacto (máx de vistas o alcance)
    def impacto(r):
        return max(r["vistas"], r["alcance"])
    top = sorted(rows, key=impacto, reverse=True)[:6]
    # Solo agregados + lo mejor de cada red. Guardar TODAS las publicaciones dejaba ficheros
    # de ~90 KB (~22k tokens) que se comen el contexto en cuanto alguien pide las métricas.
    por_red = {}
    for r in rows:
        por_red.setdefault(r["red"], []).append(r)
    top_por_red = {red: sorted(g, key=impacto, reverse=True)[:TOP_POR_RED]
                   for red, g in sorted(por_red.items())}
    return {"cliente": cli, "marca": label, "ventana_dias": DAYS, "n_total": len(rows),
            "actualizado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "por_red_formato": por_grupo, "top_posts": top, "top_por_red": top_por_red}


def write_md(s):
    L = [f"# 📊 Métricas Metricool — {s['marca']} ({s['cliente']})", ""]
    L.append(f"> Instagram (Reels+feed) + TikTok · últimos {s['ventana_dias']} días · "
             f"{s['n_total']} publicaciones · actualizado {s['actualizado']}")
    L.append("")
    if not s["n_total"]:
        L.append("_Sin datos en Metricool (¿cuentas no conectadas?)._")
        return "\n".join(L) + "\n"
    L.append("## Rendimiento por red y formato (ordenado por vistas medias)")
    L.append("")
    L.append("| Red · Formato | Nº | Vistas medias | Alcance medio | Interacc. medias | Guardados |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for k, v in s["por_red_formato"].items():
        L.append(f"| {k} | {v['n']} | {v['vistas_medias']} | {v['alcance_medio']} | "
                 f"{v['interacciones_medias']} | {v['guardados_medios']} |")
    L.append("")
    L.append("## Top publicaciones (lo que más impactó)")
    L.append("")
    for i, p in enumerate(s["top_posts"], 1):
        L.append(f"{i}. **{p['red']} · {p['formato']}** · {p['fecha']} · "
                 f"{p['vistas']} vistas · {p['alcance']} alcance · {p['interacciones']} interacc.")
        L.append(f"   - _{p['texto']}_")
        if p["url"]:
            L.append(f"   - {p['url']}")
    L.append("")
    return "\n".join(L) + "\n"


def escribir_posts(outdir, cli, rows):
    """Índice de **todas** las publicaciones, no solo el top — lo usa el termómetro.

    El resumen (`<cliente>.json`) guarda medias y top-10 por red: sirve para hablar del
    cliente, pero una pieza normal no aparece por ningún lado, así que no se puede cruzar
    una hipótesis con su número. Esto es el join: fecha + red -> vistas.
    Va en `_posts/` porque es dato de máquina; el `.md` sigue siendo lo que se lee.
    """
    destino = os.path.join(outdir, "_posts")
    os.makedirs(destino, exist_ok=True)
    datos = {"cliente": cli, "ventana_dias": DAYS,
             "actualizado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "posts": sorted(rows, key=lambda r: (r["fecha"], r["red"]))}
    with open(os.path.join(destino, f"{cli}.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


def main():
    env = load_env()
    tok = env.get("METRICOOL_API_TOKEN")
    uid = env.get("METRICOOL_USER_ID")
    if not tok or not uid:
        print("Faltan METRICOOL_API_TOKEN / METRICOOL_USER_ID en infra/.env")
        return 2
    marcas = json.load(open(os.path.join(HUB, "config/metricool-marcas.json")))["roster_v1"]
    outdir = os.path.join(HUB, "memoria/metricas")
    os.makedirs(outdir, exist_ok=True)
    ok = 0
    fallidos = []
    for cli, info in marcas.items():
        try:
            rows = fetch_all(info["brand_id"], uid, tok)
        except Exception as e:
            # No se escribe nada: se deja el fichero anterior en su sitio.
            print(f"  {cli}: ERROR {e} (conservo las métricas anteriores)")
            fallidos.append(cli)
            continue
        s = summarize(cli, info["label"], rows)
        with open(os.path.join(outdir, f"{cli}.json"), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
        with open(os.path.join(outdir, f"{cli}.md"), "w", encoding="utf-8") as f:
            f.write(write_md(s))
        escribir_posts(outdir, cli, rows)
        print(f"  {cli}: {s['n_total']} pubs -> memoria/metricas/{cli}.md")
        ok += 1
    print(f"Listo: {ok}/{len(marcas)} clientes actualizados.")
    if fallidos:
        print(f"Sin actualizar (se conserva lo anterior): {', '.join(fallidos)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
