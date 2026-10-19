#!/usr/bin/env python3
"""Coco multicanal — lo que no toca Notion: prompt, parseo/validación y archivos de la pieza.

Lo usa `infra/notion/guionizar.py` cuando una idea de Contenido RM trae `Soporte = Multicanal`
(Fase 2 de PLAN-MULTICANAL-RM-2026-10.md). Separado de guionizar.py para poder probarlo sin
Notion ni llamada al modelo:

    python3 infra/carruseles/multicanal.py --respuesta crudo.json --idea "…" --notas "…" [--out DIR] [--sin-render]
        → valida la respuesta de Coco como lo haría la corrida de noche y escribe la carpeta
    python3 infra/carruseles/multicanal.py --prompt --idea "…" --notas "…"
        → enseña el prompt que se mandaría (y su tamaño), sin llamar a nadie

Carpeta de salida: memoria/clientes/rm-agency/carruseles/<NN>-<id>/ con pieza.json, copy.md,
linkedin.md, blog.md (frontmatter de infra/web/blog.py), los PNG, el PDF y _vista.png.
Nada se publica ni se programa: eso es de Gerard.
"""
import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import carrusel  # noqa: E402

HUB = AQUI.parent.parent
RM = HUB / "memoria" / "clientes" / "rm-agency"
CARRUSELES = RM / "carruseles"
PROMPT_MD = HUB / "agentes" / "guiones" / "multicanal.md"
EJEMPLO_LINKEDIN = CARRUSELES / "04-dar-valor" / "linkedin.md"

SYSTEM_PROMPT = ("Eres Coco, la copywriter de RM Agency. Escribes en español de España, frases cortas, "
                 "sin jerga de agencia. Respondes SOLO con el JSON que se te pide, sin texto alrededor.")
# Marca del primer bloque que escribe Coco multicanal en la ficha (para re-guionizar sin pisar lo de arriba).
MARCA_INICIO = "🎠 Carrusel"


def leer(p):
    try:
        return Path(p).read_text(encoding="utf-8")
    except OSError:
        return ""


def cifras_de(*textos):
    """Números que aparecen en lo que escribió Gerard (idea + notas): la lista de verificadas.

    Hasta que exista datos_caso.py (cifras de Metricool), lo único verificado es lo que él ha
    escrito. «20.000», «2,4 M», «89.679» → se guardan tal cual; la comparación es por dígitos.
    """
    out = []
    for t in textos:
        for c in re.findall(r"\d[\d.,]*\d|\d", t or ""):
            if c not in out:
                out.append(c)
    return out


def construir_prompt(idea, notas, cifras):
    brief = leer(RM / "copy-brief.md")
    ficha = leer(RM / "ficha.md")
    ejemplo = leer(EJEMPLO_LINKEDIN)
    return (
        f"{leer(PROMPT_MD)}\n\n"
        f"=== BRIEF DE RM (manda sobre lo anterior si chocan) ===\n{brief}\n\n"
        + (f"=== FICHA DE RM ===\n{ficha}\n\n" if ficha else "")
        + (f"=== EJEMPLO DE POST DE LINKEDIN YA APROBADO (tono, no copiar) ===\n{ejemplo}\n\n" if ejemplo else "")
        + f"=== LA IDEA ===\nIDEA: {idea}\nNOTAS: {notas or '(ninguna)'}\n\n"
        f"CIFRAS VERIFICADAS (las únicas que puedes escribir): {', '.join(cifras) if cifras else '(ninguna: no escribas cifras)'}\n\n"
        "Devuelve SOLO el JSON de la sección «Salida»."
    )


def prompt_correccion(prompt, crudo, error):
    """Segunda (y última) oportunidad en la misma corrida: el mismo prompt + su respuesta + el fallo."""
    return (f"{prompt}\n\n=== TU RESPUESTA ANTERIOR ===\n{crudo}\n\n"
            f"=== NO PASÓ LA VALIDACIÓN ===\n{error}\n\n"
            "Corrige SOLO eso (sin inventar cifras: si un número no está en la lista, quítalo o dilo "
            "con palabras) y devuelve el JSON COMPLETO otra vez, sin texto alrededor.")


def _digitos(c):
    return re.sub(r"\D", "", str(c))


def cifras_fuera(texto, cifras):
    ok = {_digitos(c) for c in cifras}
    return sorted({c for c in re.findall(r"\d[\d.,]*\d", texto or "") if _digitos(c) not in ok})


def parsear(crudo, cifras):
    """JSON de Coco → dict validado. Lanza RuntimeError si no sirve (la idea vuelve a la cola).

    Devuelve {"pieza", "copy_ig", "linkedin", "blog", "apuesta", "porque", "notas", "avisos"}.
    """
    t = (crudo or "").strip()
    ini, fin = t.find("{"), t.rfind("}")
    if ini == -1 or fin == -1:
        raise RuntimeError("no encontré JSON en la respuesta")
    try:
        d = json.loads(t[ini:fin + 1])
    except ValueError as e:
        raise RuntimeError(f"JSON ilegible: {e}")
    pieza = d.get("carrusel")
    if not isinstance(pieza, dict):
        raise RuntimeError("JSON sin `carrusel`")
    pieza["estilo"] = "rm"
    pieza["id"] = re.sub(r"[^a-z0-9-]+", "-", (pieza.get("id") or "carrusel").lower()).strip("-")[:40] or "carrusel"
    pieza.pop("prefijo", None)
    pieza["cifras_verificadas"] = list(cifras)
    err, av = carrusel.validar(pieza)
    # En el carrusel, una cifra que no está verificada es error (regla dura del brief), no aviso.
    err += [a for a in av if a.startswith("cifra ")]
    av = [a for a in av if not a.startswith("cifra ")]
    if err:
        raise RuntimeError("carrusel no válido: " + "; ".join(err[:4]))
    blog = d.get("blog") or {}
    res = {
        "pieza": pieza,
        "copy_ig": (d.get("copy_ig") or "").strip(),
        "linkedin": (d.get("linkedin") or "").strip(),
        "blog": blog if isinstance(blog, dict) else {},
        "apuesta": (d.get("apuesta") or "").strip(),
        "porque": (d.get("porque") or "").strip(),
        "notas": (d.get("notas") or "").strip(),
        "avisos": av,
    }
    if not res["copy_ig"] or not res["linkedin"] or not res["blog"].get("cuerpo_md"):
        raise RuntimeError("falta copy_ig, linkedin o blog.cuerpo_md")
    # Fuera del carrusel, las cifras no verificadas se avisan bien visibles (Gerard lo revisa todo).
    for canal, txt in (("copy IG", res["copy_ig"]), ("LinkedIn", res["linkedin"]),
                       ("blog", res["blog"].get("cuerpo_md", ""))):
        fuera = cifras_fuera(txt, cifras)
        if fuera:
            res["avisos"].append(f"{canal}: cifras sin verificar {', '.join(fuera[:6])}")
    palabras = len(res["blog"].get("cuerpo_md", "").split())
    if palabras < 700:
        res["avisos"].append(f"blog corto: {palabras} palabras (objetivo 800-1.200)")
    if PRECIO_RE.search(res["copy_ig"] + res["linkedin"] + res["blog"].get("cuerpo_md", "")):
        res["avisos"].append("aparece un precio (€) en copy/LinkedIn/blog")
    return res


PRECIO_RE = carrusel.PRECIO


def siguiente_carpeta(pid, base=CARRUSELES):
    """memoria/.../carruseles/<NN>-<id>: el siguiente número tras los que ya hay (01-desliza-si…)."""
    nums = [int(m.group(1)) for p in base.glob("[0-9][0-9]-*") if (m := re.match(r"(\d\d)-", p.name))]
    # Si ya existe una carpeta con este mismo id (re-guionizar), se reutiliza.
    for p in sorted(base.glob(f"[0-9][0-9]-{pid}")):
        return p, int(p.name[:2])
    n = max(nums, default=0) + 1
    return base / f"{n:02d}-{pid}", n


def _fm(campos):
    lineas = ["---"]
    for k, v in campos.items():
        v = str(v or "").replace("\n", " ").replace('"', "'")
        lineas.append(f'{k}: "{v}"' if k in ("titulo_seo", "meta_description") else f"{k}: {v}")
    return "\n".join(lineas + ["---", ""])


def guardar(res, carpeta=None, render=True, motor="auto"):
    """Escribe la carpeta de la pieza y renderiza. Devuelve {"carpeta", "pngs", "pdf", "error_render"}."""
    pieza = res["pieza"]
    if carpeta is None:
        carpeta, n = siguiente_carpeta(pieza["id"])
    else:
        carpeta, n = Path(carpeta), 0
    carpeta.mkdir(parents=True, exist_ok=True)
    pieza["prefijo"] = f"c{n}" if n else pieza["id"]
    (carpeta / "pieza.json").write_text(json.dumps(pieza, ensure_ascii=False, indent=1), encoding="utf-8")
    (carpeta / "copy.md").write_text(_fm({"fecha": "pendiente", "estado": "borrador para revisar"})
                                     + res["copy_ig"] + "\n", encoding="utf-8")
    (carpeta / "linkedin.md").write_text(_fm({"canal": "LinkedIn (página de empresa RM Agency)", "fecha": "pendiente",
                                              "adjunto": f"{pieza['id']}.pdf", "estado": "borrador para revisar"})
                                         + res["linkedin"] + "\n", encoding="utf-8")
    b = res["blog"]
    (carpeta / "blog.md").write_text(_fm({
        "canal": "Blog rmagency.es", "estado": "borrador",
        "kw_principal": b.get("kw_principal"), "kw_secundarias": b.get("kw_secundarias"),
        "titulo_seo": b.get("titulo_seo"), "slug": b.get("slug"),
        "meta_description": b.get("meta_description"),
        "imagen_destacada": f"{pieza['prefijo']}-01.png", "categoria": b.get("categoria") or "Casos reales",
    }) + "\n" + b.get("cuerpo_md", "").strip() + "\n", encoding="utf-8")
    out = {"carpeta": carpeta, "pngs": [], "pdf": None, "error_render": None}
    if render:
        try:
            pngs, pdf, _, _ = carrusel.construir(pieza, carpeta, carpeta, motor)
            out.update(pngs=pngs, pdf=pdf)
        except (Exception, SystemExit) as e:  # noqa: BLE001 — sin navegador no se pierde el texto
            out["error_render"] = str(e) or e.__class__.__name__
    return out


# ------------------------------------------------------------------ bloques para la ficha de Notion

def _rt(txt):
    return [{"text": {"content": (txt or "—")[:1900]}}]


def _b(tipo, txt):
    return {"object": "block", "type": tipo, tipo: {"rich_text": _rt(txt)}}


def _parrafos(txt):
    return [_b("paragraph", p.strip()) for p in re.split(r"\n\s*\n", txt or "") if p.strip()]


def _md(md):
    out = []
    for bloque in re.split(r"\n\s*\n", md or ""):
        for linea in bloque.strip().split("\n") if bloque.strip().startswith(("- ", "* ")) else [bloque.strip()]:
            if not linea:
                continue
            if linea.startswith("# "):
                out.append(_b("heading_2", linea[2:]))
            elif linea.startswith(("## ", "### ")):
                out.append(_b("heading_3", linea.lstrip("#").strip()))
            elif linea.startswith(("- ", "* ")):
                out.append(_b("bulleted_list_item", linea[2:]))
            else:
                out.append(_b("paragraph", linea.replace("**", "")))
    return out


def bloques_notion(res, guardado):
    p = res["pieza"]
    filas = [f"Portada · {p['portada'].get('titular', '')}"]
    filas += [f"{i} · {d.get('titular', '')} — {d.get('apoyo', '')} [{(d.get('dibujo') or {}).get('tipo', '—')}]"
              for i, d in enumerate(p.get("diapositivas", []), start=2)]
    filas.append(f"Cierre · {p['cierre'].get('titular', '')} → comenta {p['cierre'].get('palabra', 'ESTRATEGIA')}")
    carpeta = guardado["carpeta"]
    try:
        rel = carpeta.relative_to(HUB)
    except ValueError:
        rel = carpeta
    archivos = (f"{rel}/ — {len(guardado['pngs'])} PNG + {p['id']}.pdf (LinkedIn) + copy.md, linkedin.md, blog.md"
                if not guardado["error_render"] else
                f"{rel}/ — textos guardados, pero el render FALLÓ: {guardado['error_render']}. "
                f"Rehazlo con: python3 infra/carruseles/carrusel.py --json {rel}/pieza.json --out {rel}")
    bl = [_b("heading_2", f"{MARCA_INICIO} — {len(filas)} diapositivas")]
    bl += [_b("numbered_list_item", f) for f in filas]
    bl.append({"object": "block", "type": "callout", "callout": {"icon": {"emoji": "📁"}, "rich_text": _rt(archivos)}})
    if res["avisos"] or res["notas"]:
        txt = " · ".join(res["avisos"] + ([f"Coco: {res['notas']}"] if res["notas"] else []))
        bl.append({"object": "block", "type": "callout", "callout": {"icon": {"emoji": "⚠️"}, "rich_text": _rt(txt)}})
    bl += [_b("heading_2", "📸 Copy IG / TikTok / FB")] + _parrafos(res["copy_ig"])
    bl += [_b("heading_2", "💼 LinkedIn")] + _parrafos(res["linkedin"])
    b = res["blog"]
    bl += [_b("heading_2", "📝 Blog (borrador)"),
           _b("paragraph", f"SEO: {b.get('titulo_seo', '')} · /{b.get('slug', '')} · {b.get('meta_description', '')}")]
    bl += _md(b.get("cuerpo_md", ""))
    if res["apuesta"] or res["porque"]:
        bl += [_b("heading_2", "🎯 Qué estamos probando"), _b("paragraph", f"{res['apuesta']}\n\nPor qué: {res['porque']}")]
    return bl


def main():
    ap = argparse.ArgumentParser(description="Prueba offline de Coco multicanal (sin Notion ni modelo).")
    ap.add_argument("--respuesta", help="archivo con la respuesta cruda de Coco (el JSON)")
    ap.add_argument("--prompt", action="store_true", help="enseña el prompt que se mandaría")
    ap.add_argument("--idea", default="")
    ap.add_argument("--notas", default="")
    ap.add_argument("--out", help="carpeta de salida (por defecto, la siguiente NN- en carruseles de RM)")
    ap.add_argument("--sin-render", action="store_true")
    a = ap.parse_args()
    cifras = cifras_de(a.idea, a.notas)
    if a.prompt:
        p = construir_prompt(a.idea, a.notas, cifras)
        print(p)
        print(f"\n--- {len(p)} caracteres (~{len(p) // 4} tokens) · cifras verificadas: {cifras}", file=sys.stderr)
        return 0
    if not a.respuesta:
        ap.error("--respuesta o --prompt")
    try:
        res = parsear(Path(a.respuesta).read_text(encoding="utf-8"), cifras)
    except RuntimeError as e:
        print(f"❌ {e}")
        return 1
    for x in res["avisos"]:
        print(f"⚠️  {x}")
    g = guardar(res, a.out, not a.sin_render)
    print(f"✓ {g['carpeta']} · {len(g['pngs'])} PNG" + (f" · render falló: {g['error_render']}" if g["error_render"] else ""))
    print(f"  {len(bloques_notion(res, g))} bloques para la ficha de Notion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
