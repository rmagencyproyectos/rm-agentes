#!/usr/bin/env python3
"""Genera el copy de redes con Coco, a demanda (para el botón de la app Pocket).

Recibe JSON por stdin y devuelve JSON por stdout:
    entrada: {"clientId": "golossa", "title": "...", "format": "Reel", "indicaciones": "opcional"}
    salida:  {"ok": true, "copy": "..."}  |  {"ok": false, "error": "..."}

Reutiliza el mismo patrón que autoprogramar.py (claude -p headless, sin herramientas,
con el brief del cliente). Si el usuario pasa `indicaciones`, se le dan a Coco como
guía extra (tono, promo, CTA, lo que quiera). Interpretador: /usr/bin/python3.
"""
import json
import os
import shutil
import subprocess
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
MODELO = "claude-sonnet-5"
PRESUPUESTO_USD = "0.20"


def claude_bin():
    """Localiza el ejecutable claude aunque el proceso no herede el PATH del terminal
    (p. ej. si el servidor se lanzó con doble clic en start.command)."""
    b = shutil.which("claude")
    if b:
        return b
    home = os.path.expanduser("~")
    for p in (f"{home}/.local/node/bin/claude", f"{home}/.local/bin/claude",
              "/usr/local/bin/claude", "/opt/homebrew/bin/claude", f"{home}/.claude/local/claude"):
        if os.path.exists(p):
            return p
    return "claude"  # último recurso: que lo intente por PATH

# clientId corto de la app -> slug del hub (resto coinciden 1-a-1).
ALIAS = {"jesus": "jesus-mora", "xavi": "xavi-colomina"}


def roster():
    marcas = json.load(open(os.path.join(HUB, "config/metricool-marcas.json")))["roster_v1"]
    return {slug: m.get("label", slug) for slug, m in marcas.items()}


def leer(*p):
    try:
        with open(os.path.join(*p), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def contexto_cliente(slug):
    base = os.path.join(HUB, "memoria/clientes", slug)
    partes = [f"### {n}\n{leer(base, n)}" for n in ("copy-brief.md", "ficha.md") if leer(base, n)]
    return "\n\n".join(partes) or "(sin brief; usa un tono cercano y natural, el estándar del cliente)"


def prompt_copy(titulo, fmt, slug, label, indicaciones):
    extra = ""
    if indicaciones and indicaciones.strip():
        extra = (f"\n=== INDICACIONES DE GERARD (respétalas) ===\n{indicaciones.strip()}\n")
    return (
        f"Eres Coco, la copywriter de RM Agency. Escribe el **copy de redes** (Instagram/TikTok) "
        f"para este {fmt or 'Reel'} de **{label}**.\n\n"
        f"IDEA / TÍTULO DE LA PIEZA: {titulo}\n"
        f"{extra}\n"
        f"=== MARCA Y TONO ===\n{contexto_cliente(slug)}\n\n"
        "Reglas (de Gerard, 22/09/2026 — la longitud manda sobre el brief): CORTO, 25-50 "
        "palabras de cuerpo sin contar hashtags, 2-4 líneas. SEO: la palabra clave principal "
        "(lo que alguien buscaría para encontrar este vídeo) en la primera línea, natural, sin "
        "keyword stuffing. NO repitas lo que se dice o se ve en el vídeo: aporta el porqué, el "
        "contexto o un dato que el vídeo no da. CTA natural solo si el brief la permite. "
        "Hashtags: los del brief; si no dice nada, 3-5 relevantes al final. Emojis con "
        "moderación. NADA de explicaciones ni comillas.\n"
        "Devuelve SOLO el texto del copy, listo para pegar en el post."
    )


def coco_copy(titulo, fmt, slug, label, indicaciones):
    proc = subprocess.run(
        [claude_bin(), "-p", "--model", MODELO, "--tools", "", "--disable-slash-commands",
         "--no-session-persistence", "--max-budget-usd", PRESUPUESTO_USD, "--output-format", "json"],
        input=prompt_copy(titulo, fmt, slug, label, indicaciones),
        capture_output=True, text=True, timeout=180)
    # Intenta leer el JSON de salida aunque el código de salida no sea 0 (claude
    # devuelve el detalle del error ahí, p. ej. "Not logged in").
    d = {}
    try:
        d = json.loads(proc.stdout or "{}")
    except Exception:
        d = {}
    result = str(d.get("result") or "")
    if "logged in" in result.lower() or "/login" in result.lower():
        raise RuntimeError("El CLI de Claude no está logueado en este Mac. Ábrelo una vez "
                           "(ejecuta `claude` en la Terminal y haz login) y vuelve a intentarlo.")
    if proc.returncode != 0:
        raise RuntimeError(result[:200] or f"claude salió {proc.returncode}: {proc.stderr[:200]}")
    if d.get("is_error") or d.get("subtype") != "success":
        raise RuntimeError(f"claude error: {d.get('subtype')} {result[:200]}")
    return result.strip().strip('"').strip()


def main():
    try:
        inp = json.loads(sys.stdin.read() or "{}")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"JSON de entrada inválido: {e}"})); return 2

    titulo = (inp.get("title") or "").strip()
    if not titulo:
        print(json.dumps({"ok": False, "error": "Falta el título de la idea"})); return 2
    fmt = inp.get("format") or "Reel"
    cid = inp.get("clientId") or ""
    slug = ALIAS.get(cid, cid)
    label = roster().get(slug, inp.get("clientName") or slug or "la marca")

    try:
        copy = coco_copy(titulo, fmt, slug, label, inp.get("indicaciones") or "")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)); return 1
    print(json.dumps({"ok": True, "copy": copy, "slug": slug, "label": label}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
