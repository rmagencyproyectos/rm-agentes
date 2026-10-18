#!/usr/bin/env python3
"""Etiqueta las piezas de una base de rendimiento a partir de SU COPY, y lo deja dicho.

Por qué existe (29/09/2026): Gerard etiquetó a mano las 34 piezas que mejor funcionaron de
Golossa. Con solo ganadores etiquetados **no se puede medir nada**: toda etiqueta parece
ganadora porque no hay grupo de comparación. Esto etiqueta el resto para que lo haya.

⚠️ Lo honesto de este script es su límite: **solo ve el copy, no el vídeo**. Por eso:
  - cada fila que toca queda marcada `Etiquetado por = Deducido del copy`, separada de las que
    marcó Gerard viendo la pieza;
  - cuando el copy no dice de qué va el vídeo, **deja la etiqueta vacía** en vez de rellenarla
    por rellenar. Una etiqueta inventada no es un dato: es ruido que además parece un dato.
Al analizar, se puede exigir "solo las de Gerard" o contar las dos y comparar.

Las opciones salen EN VIVO del esquema de la base: si Gerard añadió "lo que se dice vs lo que
se piensa", el clasificador la puede usar. No inventa opciones nuevas.

Uso:
  etiquetar_desde_copy.py --db <database_id> [--max N] [--lote 15] [--dry-run] [--solo-vacias]
Salida: 0 ok · 2 falta token/config · 1 error
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

import notion_api as na

MODELO = "claude-sonnet-5"
PRESUPUESTO_USD = "0.40"     # por lote
CAMPOS = ("Tipo de idea", "Formato", "Plantilla", "Palanca")


TIPOS = {}   # campo -> select | multi_select (cada base lo tiene a su manera)


def opciones(db, tok):
    # Lo que el etiquetado automático no usa (Oficio: sale siempre, no distingue): config/etiquetas.json.
    sys.path.insert(0, os.path.join(na.HUB, "infra/analisis"))
    import etiquetas as E
    fuera = E.config().get("no_inferir", {})
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    out = {}
    for c in CAMPOS:
        p = props.get(c) or {}
        tipo = p.get("type")
        TIPOS[c] = tipo
        out[c] = [o["name"] for o in (p.get(tipo) or {}).get("options", [])
                  if o["name"] not in fuera.get(c, [])] if tipo in ("select", "multi_select") else []
    return out


def pendientes(db, tok, solo_vacias=True):
    filas = []
    for pg in na.query(db, tok):
        p = pg["properties"]
        tiene = any((p.get(c) or {}).get("multi_select") or (p.get(c) or {}).get("select")
                    for c in CAMPOS)
        if tiene and solo_vacias:
            continue
        # Ni lo ya visto (Gemini/Gerard), ni lo que aún no se ha publicado.
        fecha = (na.plain(p.get("Fecha")) or "")[:10]
        if (na.plain(p.get("Etiquetado por")) or "") or na.plain(p.get("Estado")) == "Pendiente" \
                or not fecha or fecha > datetime.date.today().isoformat():
            continue
        filas.append({"id": pg["id"], "titulo": na.plain(p.get("Pieza")),
                      "fecha": (na.plain(p.get("Fecha")) or "")[:10],
                      "copy": na.plain(p.get("Copy")) or ""})
    return filas


def prompt(lote, ops):
    piezas = "\n\n".join(
        f'[{i}] fecha {x["fecha"]}\nCOPY: """{(x["copy"] or x["titulo"])[:900]}"""'
        for i, x in enumerate(lote))
    listas = "\n".join(f"- {c}: {', '.join(v) or '(sin opciones)'}" for c, v in ops.items())
    return (
        "Clasifica piezas de contenido de redes de una pastelería (Golossa) para poder medir "
        "qué formatos funcionan.\n\n"
        "⚠️ REGLA DURA: solo tienes el COPY, no el vídeo. Si el copy no deja claro qué pasa en "
        "la pieza, deja la etiqueta VACÍA (lista vacía). Una etiqueta inventada estropea la "
        "medición más que una etiqueta que falta. Es normal y correcto devolver campos vacíos.\n\n"
        "Usa SOLO estas opciones, tal cual están escritas (no inventes ninguna):\n"
        f"{listas}\n\n"
        "Criterios:\n"
        "- `Tipo de idea`: de qué va (Humor, Producto, Educativa, Caso real, Receta…).\n"
        "- `Formato`: la forma en que se cuenta (Trend, Explicacion, Proceso, Receta, "
        "'lo que se dice vs lo que se piensa'…).\n"
        "- `Plantilla`: la mecánica de guion, solo si el copy la delata sin dudas.\n"
        "- `Palanca`: qué resorte usa (Curiosidad, Deseo, Humor, Identificación…).\n"
        "Puedes poner varias por campo cuando encajen varias, pero no las amontones: 1-2 es lo normal.\n\n"
        f"PIEZAS:\n{piezas}\n\n"
        'Devuelve SOLO un JSON: {"piezas": [{"i": 0, "tipo_idea": [], "formato": [], '
        '"plantilla": [], "palanca": []}, ...]} con una entrada por pieza, sin texto alrededor.'
    )


def clasificar(lote, ops):
    proc = subprocess.run(
        ["claude", "-p", "--model", MODELO, "--tools", "", "--disable-slash-commands",
         "--no-session-persistence", "--max-budget-usd", PRESUPUESTO_USD, "--output-format", "json"],
        input=prompt(lote, ops), capture_output=True, text=True, timeout=300)
    try:
        d = json.loads(proc.stdout)
    except Exception:
        raise RuntimeError(f"claude salió {proc.returncode}: {proc.stderr[:200]}")
    if proc.returncode != 0 or d.get("is_error") or d.get("subtype") != "success":
        raise RuntimeError(f"claude: {d.get('terminal_reason') or d.get('subtype')}")
    t = (d.get("result") or "").strip()
    ini, fin = t.find("{"), t.rfind("}")
    if ini == -1:
        raise RuntimeError("sin JSON en la respuesta")
    return json.loads(t[ini:fin + 1]).get("piezas", [])


def main():
    ap = argparse.ArgumentParser(description="Etiqueta desde el copy (y lo deja marcado).")
    ap.add_argument("--db", required=True)
    ap.add_argument("--max", type=int, default=250)
    ap.add_argument("--lote", type=int, default=15)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--solo-vacias", action="store_true", default=True)
    a = ap.parse_args()

    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    ops = opciones(a.db, tok)
    cola = pendientes(a.db, tok, a.solo_vacias)[:a.max]
    print(f"{len(cola)} piezas sin etiquetar · lotes de {a.lote}")
    if a.dry_run:
        for x in cola[:5]:
            print(f"  {x['fecha']} {x['titulo'][:60]}")
        return 0

    claves = {"Tipo de idea": "tipo_idea", "Formato": "formato",
              "Plantilla": "plantilla", "Palanca": "palanca"}
    hechas, vacias = 0, 0
    for i in range(0, len(cola), a.lote):
        lote = cola[i:i + a.lote]
        try:
            res = clasificar(lote, ops)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            sys.stderr.write(f"✗ lote {i // a.lote + 1}: {e}\n")
            continue
        for r in res:
            idx = r.get("i")
            if not isinstance(idx, int) or idx >= len(lote):
                continue
            props = {}
            for campo, clave in claves.items():
                vals = [v for v in (r.get(clave) or []) if v in ops[campo]]
                if vals:
                    props[campo] = (na.prop_multi(vals[:3]) if TIPOS.get(campo) == "multi_select"
                                    else na.prop_select(vals[0]))
            if not props:
                vacias += 1
                continue
            props["Etiquetado por"] = na.prop_select("Deducido del copy")
            try:
                na.update_props(lote[idx]["id"], tok, props)
                hechas += 1
            except RuntimeError as e:
                sys.stderr.write(f"✗ {lote[idx]['titulo'][:40]}: {e}\n")
        print(f"  lote {i // a.lote + 1}: {hechas} etiquetadas · {vacias} sin señal en el copy")
    print(f"✓ {hechas} etiquetadas desde el copy · {vacias} se quedan vacías (el copy no dice)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
