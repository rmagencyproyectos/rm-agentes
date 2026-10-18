#!/usr/bin/env python3
"""Datos del panel "Qué vídeos hacer": qué funciona en la agencia y en cada cliente. 0 tokens.

Pedido por Gerard el 02/10/2026. Lee las bases "📊 Rendimiento de vídeos" de cada cliente
(`rendimiento_db` en config/notion-bases.json), pone a todos los vídeos la MISMA nota
(`nota.py`: vistas + interacción contra lo normal de su cliente) y agrega por las etiquetas
comunes de `agentes/guiones/ETIQUETAS.md` (+ lo propio de cada cliente en config/etiquetas.json).

De dónde salen las etiquetas (`etiquetas_viven_en`):
  - rendimiento → en la propia fila (Golossa, Jesús, NewMos).
  - contenido   → en la ficha de la base de Contenido enlazada por "Pieza de producción"
                  (Xavi: su base de rendimiento solo las trae por rollup y le falta Formato).

Reglas de lectura (las mismas del termómetro):
  - Un vídeo con menos de 14 días no cuenta: aún no ha terminado de rodar.
  - Menos de 3 vídeos detrás de una etiqueta = "no concluye". Se enseña, pero en gris.
  - Haz más: mediana ≥ 1.2. Evita: mediana < 0.9 Y pega (nota ≥ 1.2) menos que la media
    de los vídeos — medido el 02/10: las medianas se aprietan en 0.85-1.0 (los virales tiran
    de la media, no de la mediana), así que un corte en 0.8 no marcaba nada.
  - El ranking usa una nota AJUSTADA que acerca a 1.0 lo que tiene pocos vídeos
    ((mediana·n + 1·5) / (n + 5)): sin eso, 3 vídeos con 5.8 ganaban a 22 con 4.0.
  - Lo que solo ha funcionado en UN cliente se marca: no es lo mismo que algo probado en tres.

Salidas (memoria/analisis/):
  panel.json        lo que pinta la página (infra/analisis/panel.html)
  ../infra/analisis/web/   la web lista para publicar: panel.html + datos.json + fuentes.
                    La sube cada mañana la tarea programada «Panel: publicar» (app de Claude).
  general.md        el ranking de la agencia, legible
  <cliente>.md      haz más / evita / top / peores — lo lee Oli al montar la tanda

Uso:  panel_datos.py [--dry-run]      (--dry-run: imprime el resumen, no escribe)
Salida: 0 ok · 2 falta token · 1 error
"""
import base64
import shutil
import datetime
import json
import os
import statistics
import sys
from itertools import combinations

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etiquetas as E  # noqa: E402
import nota as N  # noqa: E402
import notion_api as na  # noqa: E402

SALIDA = os.path.join(HUB, "memoria/analisis")
DIMS = ("Tipo de idea", "Formato", "Palanca", "Plantilla")
COMBOS = (("Tipo de idea", "Formato"), ("Formato", "Palanca"))
MIN_DIAS, MIN_N, ALTO, BAJO, PESO = 14, 3, 1.2, 0.9, 5
# Qué tan fiable es la etiqueta. "vistos" = alguien vio el vídeo (Gerard o Gemini).
VISTOS = ("Gerard", "Gemini")


def cargar_cfg():
    etq = E.config()
    cfg = na.load_config()
    clientes = {}
    for grupo, activo in (("clientes", True), ("exclientes", False)):
        for slug, c in cfg.get(grupo, {}).items():
            if c.get("rendimiento_db"):
                clientes[slug] = {**c, "activo": activo}
    activos = [s for s, c in cfg["clientes"].items() if s != "rm-agency"]
    return etq, clientes, activos, {s: c["label"] for g in ("clientes", "exclientes")
                                    for s, c in cfg.get(g, {}).items()}


def lista(props, k):
    v = na.plain(props.get(k))
    if v in (None, ""):
        return []
    return v if isinstance(v, list) else [v]


def texto(props, *claves):
    for k in claves:
        v = na.plain(props.get(k))
        if v:
            return v if isinstance(v, str) else ", ".join(map(str, v))
    return ""


def fecha_de(props):
    v = na.plain(props.get("Fecha"))
    return (v or "")[:10]


VOCAB = {k: set(v) for k, v in E.listas().items()}


def leer_cliente(slug, c, etq, tok):
    """Una fila por vídeo publicado y con 14+ días, ya con etiquetas comunes y nota."""
    filas = na.query(c["rendimiento_db"], tok)
    donde = etq.get("etiquetas_viven_en", {}).get(slug, "rendimiento")
    contenido = {}
    if donde == "contenido":
        for pg in na.query(c["database_id"], tok):
            contenido[pg["id"].replace("-", "")] = pg["properties"]
    extras = etq.get("extras_por_cliente", {}).get(slug, [])
    hoy = datetime.date.today()
    videos = []
    for pg in filas:
        p = pg["properties"]
        if texto(p, "Estado") == "Pendiente":
            continue
        f = fecha_de(p)
        if not f or (hoy - datetime.date.fromisoformat(f)).days < MIN_DIAS:
            continue
        redes = N.redes_de(p)
        if not redes:
            continue
        fuente_etq = p
        if donde == "contenido":
            rel = (p.get("Pieza de producción") or {}).get("relation") or []
            fuente_etq = contenido.get(rel[0]["id"].replace("-", ""), {}) if rel else {}
        v = {
            "cliente": slug,
            "titulo": texto(p, "Pieza")[:140],
            "fecha": f,
            "redes": redes,
            "url": texto(p, "IG URL") or texto(p, "TT URL", "TikTok URL") or texto(p, "YouTube URL"),
            "por_que": texto(p, "Por qué funciona (vídeo)", "Por que funciona?", "Qué ha pasado (revisión)", "Qué ha pasado (auto)")[:400],
            "fuente": texto(fuente_etq, "Etiquetado por") or texto(p, "Etiquetado por") or "Sin dato",
            # Solo lo que está en ETIQUETAS.md: una opción retirada (Emoción) no puede salir
            # como "ganadora" por las filas que aún la arrastran.
            "etiquetas": {d: [x for x in lista(fuente_etq, d) if x in VOCAB[d]] for d in DIMS},
            "extras": {e: lista(p, e) for e in extras},
        }
        videos.append(v)
    med_v, med_e = N.medianas([v["redes"] for v in videos])
    for v in videos:
        v["nota"], v["ratio_vistas"], v["ratio_inter"] = N.nota(v["redes"], med_v, med_e)
        v["vistas"] = sum(x for x, _ in v["redes"].values())
        v["redes"] = sorted(v["redes"])
    return videos


def visto(v):
    return v["fuente"].startswith(VISTOS)


def resumen(notas):
    m = statistics.median(notas)
    n = len(notas)
    return {"mediana": round(m, 2), "n": n, "ajustada": round((m * n + PESO) / (n + PESO), 2),
            "pega": round(sum(x >= ALTO for x in notas) / n, 2)}


def veredicto(r, base_pega):
    if r["n"] < MIN_N:
        return "no concluye"
    if r["mediana"] >= ALTO:
        return "haz más"
    if r["mediana"] < BAJO and r["pega"] < base_pega:
        return "evita"
    return "normal"


def ejemplo(v):
    return {k: v[k] for k in ("cliente", "titulo", "fecha", "url", "nota", "vistas", "por_que")}


def claves_de(v):
    """Las etiquetas sueltas y las combinaciones de un vídeo, como 'Dim: valor'."""
    out = []
    for d in DIMS:
        out += [(d, x) for x in v["etiquetas"][d]]
    for a, b in COMBOS:
        out += [(f"{a} + {b}", f"{x} + {y}") for x in v["etiquetas"][a] for y in v["etiquetas"][b]]
    return out


def agregar(videos, activos):
    notas = [v["nota"] for v in videos if v["nota"]]
    base_pega = sum(x >= ALTO for x in notas) / len(notas) if notas else 0
    grupos = {}
    for v in videos:
        if not v["nota"]:
            continue
        for clave in claves_de(v):
            grupos.setdefault(clave, []).append(v)
    out = []
    for (dim, val), vs in grupos.items():
        r = resumen([v["nota"] for v in vs])
        por_cliente = {}
        for c in sorted({v["cliente"] for v in vs}):
            por_cliente[c] = resumen([v["nota"] for v in vs if v["cliente"] == c])
        ganadores = [c for c, x in por_cliente.items() if x["mediana"] >= ALTO]
        out.append({
            "dimension": dim, "valor": val, **r, "veredicto": veredicto(r, base_pega),
            "por_cliente": por_cliente,
            "solo_un_cliente": len(por_cliente) == 1,
            "gana_en": ganadores,
            "sin_probar": [c for c in activos if c not in por_cliente],
            "ejemplos": [ejemplo(v) for v in sorted(vs, key=lambda x: -x["nota"])[:3]],
            "peores": [ejemplo(v) for v in sorted(vs, key=lambda x: x["nota"])[:2]],
        })
    return sorted(out, key=lambda x: (-(x["n"] >= MIN_N), -x["ajustada"]))


def por_cliente(videos, slug, extras):
    vs = [v for v in videos if v["cliente"] == slug and v["nota"]]
    dims = [x for x in agregar(vs, []) if " + " not in x["dimension"]]
    notas = [v["nota"] for v in vs]
    base_pega = sum(x >= ALTO for x in notas) / len(notas) if notas else 0
    ext = {}
    for e in extras:
        acc = {}
        for v in vs:
            for x in v["extras"].get(e, []):
                acc.setdefault(x, []).append(v["nota"])
        ext[e] = sorted(({"valor": k, **resumen(n), "veredicto": veredicto(resumen(n), base_pega)}
                         for k, n in acc.items()), key=lambda x: -x["ajustada"])
    orden = sorted(vs, key=lambda x: -x["nota"])
    etiquetados = sum(any(v["etiquetas"][d] for d in DIMS) for v in vs)
    return {
        "videos": len(vs), "etiquetados": etiquetados, "vistos": sum(map(visto, vs)),
        "dimensiones": dims, "extras": ext,
        "top": [ejemplo(v) | {"etiquetas": v["etiquetas"]} for v in orden[:5]],
        "peores": [ejemplo(v) | {"etiquetas": v["etiquetas"]} for v in orden[::-1][:5]],
    }


def decisiones(tok, cfg_notion, slugs):
    """Últimos motivos de Gerard al aprobar/descartar, por cliente. El botón Adaptar se los
    pasa a Claude para no repetir lo que ya rechazó (y Oli los lee por su lado)."""
    out = {s: [] for s in slugs}
    filtro = {"or": [{"property": "Estado", "select": {"equals": "Descartada"}},
                     {"property": "Notas", "rich_text": {"contains": "Aceptada:"}}]}
    for pg in na.query(cfg_notion["bandeja"]["database_id"], tok, filtro):
        p = pg["properties"]
        slug, notas = na.plain(p.get("Cliente")), na.plain(p.get("Notas")) or ""
        if slug in out and notas:
            out[slug].append({"idea": (na.plain(p.get("Idea")) or "")[:120],
                              "estado": na.plain(p.get("Estado")), "motivo": notas[:300],
                              "fecha": pg.get("last_edited_time", "")[:10]})
    return {s: sorted(v, key=lambda x: x["fecha"], reverse=True)[:12] for s, v in out.items()}


def ficha_corta(slug):
    ruta = os.path.join(HUB, "memoria/clientes", slug, "ficha.md")
    try:
        with open(ruta, encoding="utf-8") as f:
            return f.read()[:2500]
    except FileNotFoundError:
        return ""


def md_general(general, labels):
    L = ["# 🧭 Qué funciona en la agencia", "",
         f"> Generado por `infra/analisis/panel_datos.py` · {datetime.date.today()}",
         "> Nota 1.0 = un vídeo normal de SU cliente (vistas + interacción). Menos de 3 vídeos no concluye.", ""]
    for titulo, ver in (("## ✅ Haz más", "haz más"), ("## ⛔ Evita", "evita")):
        L += [titulo, ""]
        items = [x for x in general if x["veredicto"] == ver]
        if ver == "evita":
            items.sort(key=lambda x: x["ajustada"])
        for g in items[:15]:
            donde = ", ".join(f"{labels.get(c, c)} {x['mediana']}" for c, x in g["por_cliente"].items())
            aviso = " · ⚠️ solo en un cliente" if g["solo_un_cliente"] else ""
            L.append(f"- **{g['valor']}** ({g['dimension']}) — nota {g['mediana']} sobre {g['n']} vídeos ({donde}){aviso}")
        L.append("")
    return "\n".join(L)


def md_cliente(slug, label, c):
    L = [f"# 🎯 Qué vídeos hacer — {label}", "",
         f"> Generado por `infra/analisis/panel_datos.py` · {datetime.date.today()} · "
         f"{c['videos']} vídeos medidos, {c['etiquetados']} etiquetados, {c['vistos']} vistos (Gerard/Gemini)", ""]
    for titulo, ver in (("## ✅ Haz más", "haz más"), ("## ⛔ Evita", "evita")):
        L += [titulo, ""]
        items = [x for x in c["dimensiones"] if x["veredicto"] == ver]
        L += [f"- **{x['valor']}** ({x['dimension']}) — nota {x['mediana']} sobre {x['n']} vídeos" for x in items] or ["- (nada concluyente todavía)"]
        L.append("")
    for titulo, clave in (("## 🏆 Los 5 mejores", "top"), ("## 🔻 Los 5 peores", "peores")):
        L += [titulo, ""]
        for v in c[clave]:
            etq = " · ".join(x for d in DIMS for x in v["etiquetas"][d]) or "sin etiquetar"
            L.append(f"- nota {v['nota']} · {v['fecha']} · {v['titulo'][:80]} — _{etq}_")
        L.append("")
    return "\n".join(L)


def leer_propuestas():
    ruta = os.path.join(SALIDA, "propuestas.json")
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def construir_html(panel):
    """Deja la web lista para publicar en infra/analisis/web/ (08/10/2026):
    panel.html (ligera, logo dentro) + datos.json + las dos fuentes de la marca RM.
    La tarea programada diaria «Panel: publicar» sube datos.json al mismo enlace."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    web, marca = os.path.join(aqui, "web"), os.path.join(aqui, "marca")
    os.makedirs(web, exist_ok=True)
    with open(os.path.join(aqui, "panel_plantilla.html"), encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(marca, "logo-rm.png"), "rb") as fh:
        html = html.replace("__LOGO__", base64.b64encode(fh.read()).decode())
    with open(os.path.join(web, "panel.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(web, "datos.json"), "w", encoding="utf-8") as f:
        json.dump(panel, f, ensure_ascii=False)
    for fuente in ("GlacialIndifference-Regular.otf", "GlacialIndifference-Bold.otf"):
        shutil.copyfile(os.path.join(marca, fuente), os.path.join(web, fuente))


def main():
    dry = "--dry-run" in sys.argv
    try:
        tok = na.token()
    except RuntimeError as e:
        print(e)
        return 2
    etq, clientes, activos, labels = cargar_cfg()
    videos = []
    for slug, c in clientes.items():
        vs = leer_cliente(slug, c, etq, tok)
        print(f"{slug}: {len(vs)} vídeos medidos (14+ días)")
        videos += vs
    general = {"todo": agregar(videos, activos),
               "vistos": agregar([v for v in videos if visto(v)], activos)}
    panel = {
        "generado": datetime.datetime.now().isoformat(timespec="minutes"),
        "umbrales": {"min_n": MIN_N, "alto": ALTO, "bajo": BAJO, "min_dias": MIN_DIAS},
        "clientes": {s: {"label": labels.get(s, s), "activo": c["activo"],
                         "ficha": ficha_corta(s),
                         **por_cliente(videos, s, etq.get("extras_por_cliente", {}).get(s, []))}
                     for s, c in clientes.items()},
        "activos_sin_datos": [s for s in activos if s not in clientes],
        "labels": labels,
        "general": general,
        "decisiones": decisiones(tok, na.load_config(), activos),
        "listas": E.listas_automaticas(),
        "glosario": E.glosario(),
        # Propuestas escritas a mano (por Claude en sesión, tras analizar todo): no se generan solas.
        "propuestas": leer_propuestas(),
        "bandeja_ds": na.load_config()["bandeja"]["data_source_id"],
        # Un punto por vídeo para los gráficos (dispersión, evolución, comparador). Compacto.
        "videos": [{"c": v["cliente"], "t": v["titulo"][:90], "u": v["url"], "f": v["fecha"],
                    "rv": v["ratio_vistas"], "ri": v["ratio_inter"], "n": v["nota"], "vi": v["vistas"],
                    "visto": visto(v), **{k: v["etiquetas"][d] for k, d in
                                          (("ti", "Tipo de idea"), ("fo", "Formato"), ("pa", "Palanca"), ("pl", "Plantilla"))}}
                   for v in videos if v["nota"]],
    }
    gm = md_general(general["todo"], labels)
    if dry:
        print("\n" + gm)
        for s, c in panel["clientes"].items():
            print(f"{s}: {c['videos']} vídeos · {c['etiquetados']} etiquetados · {c['vistos']} vistos")
        return 0
    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, "panel.json"), "w", encoding="utf-8") as f:
        json.dump(panel, f, ensure_ascii=False, indent=1)
    with open(os.path.join(SALIDA, "general.md"), "w", encoding="utf-8") as f:
        f.write(gm + "\n")
    for s, c in panel["clientes"].items():
        with open(os.path.join(SALIDA, f"{s}.md"), "w", encoding="utf-8") as f:
            f.write(md_cliente(s, c["label"], c) + "\n")
    construir_html(panel)
    print(f"✓ panel.json + panel.html + general.md + {len(panel['clientes'])} fichas en memoria/analisis/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
