#!/usr/bin/env python3
"""Limpia las etiquetas (Tipo de idea · Formato · Plantilla · Palanca · Soporte) en TODAS las bases.

Pedido por Gerard el 02/10/2026: las columnas se solapaban —Humor, Caso real, Receta, Día de
trabajo y Predicción estaban en dos a la vez— así que la misma cosa cabía en dos sitios y lo
medido no significaba nada. Las fronteras y las listas definitivas están en
`agentes/guiones/ETIQUETAS.md`; este script las APLICA.

Hace tres cosas, en este orden (importa):
  1. **Reescribe las filas** ya etiquetadas con el mapa de equivalencias. El mapa puede mover
     una etiqueta DE COLUMNA (p. ej. `Formato: Predicción` → `Palanca: Predicción`), no solo
     renombrarla.
  2. **Deja el esquema** de cada base con la lista cerrada y nada más.
  3. Avisa de lo que no sabe mapear, en vez de tirarlo en silencio.

Por qué primero las filas: al quitar una opción del esquema, Notion la borra de las páginas que
la tuvieran. Si se hiciera al revés se perderían las 253 piezas etiquetadas de Golossa.

Uso:
  etiquetas_sincronizar.py --dry-run        enseña el plan, no toca nada
  etiquetas_sincronizar.py                  lo aplica en Bandeja + bases de cliente
  etiquetas_sincronizar.py --db <id>        además, una base suelta (p. ej. la de rendimiento)
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import os
import sys

import etiquetas_idea as ei
import notion_api as na

CAMPOS = ("Tipo de idea", "Formato", "Plantilla", "Palanca", "Soporte")
PLANTILLAS_DIR = os.path.join(na.HUB, "agentes/guiones/plantillas")

# --- Listas definitivas (ETIQUETAS.md manda; Plantilla sale de la carpeta) ------------------
sys.path.insert(0, os.path.join(na.HUB, "infra/analisis"))
import etiquetas as _etq  # noqa: E402  — lee las listas de agentes/guiones/ETIQUETAS.md
_L = _etq.listas()   # ya no se copian aquí: ETIQUETAS.md manda (02/10/2026)
TIPO_IDEA, FORMATO, PALANCA, SOPORTE = (_L["Tipo de idea"], _L["Formato"], _L["Palanca"], _L["Soporte"])

# --- Equivalencias: (columna vieja, valor viejo) -> (columna nueva, valor nuevo) o None ------
# None = se descarta (no había nada que conservar). Mover de columna está permitido.
MAPA = {
    ("Tipo de idea", "Educativa"): ("Tipo de idea", "Oficio"),
    ("Tipo de idea", "Receta"): ("Formato", "Paso a paso"),
    ("Tipo de idea", "Detrás de cámaras"): ("Tipo de idea", "Día de trabajo"),
    ("Tipo de idea", "Dia de trabajo"): ("Tipo de idea", "Día de trabajo"),
    ("Tipo de idea", "Caso real"): ("Tipo de idea", "Cliente"),
    ("Tipo de idea", "Ubicacion"): ("Tipo de idea", "Local y zona"),
    ("Tipo de idea", "Tendencia"): ("Formato", "Trend"),
    ("Tipo de idea", "Regalar producto calle"): ("Formato", "A pie de calle"),
    ("Tipo de idea", "Storytelling"): ("Tipo de idea", "Cliente"),
    ("Formato", "Ranking"): ("Formato", "Lista / Top"),
    ("Formato", "Top 10"): ("Formato", "Lista / Top"),
    ("Formato", "Lista"): ("Formato", "Lista / Top"),
    ("Formato", "Receta"): ("Formato", "Paso a paso"),
    ("Formato", "Explicacion"): ("Formato", "Explicación"),
    ("Formato", "interactivo espectador"): ("Formato", "Reto al espectador"),
    ("Formato", "interaccion calle"): ("Formato", "A pie de calle"),
    ("Formato", "Foodporn"): ("Formato", "Producto en primer plano"),
    ("Formato", "Dia de trabajo"): ("Tipo de idea", "Día de trabajo"),
    ("Formato", "Predicción"): ("Palanca", "Predicción"),
    ("Formato", "lo que se dice vs lo que se piensa"): ("Plantilla", "dicho-vs-pensado"),
    ("Formato", "realidad exagerada"): ("Plantilla", "realidad-exagerada"),
    ("Palanca", "Inesperado"): ("Palanca", "Sorpresa"),
    ("Palanca", "Humor"): ("Tipo de idea", "Humor"),
    ("Palanca", "Emoción"): None,   # retirada 02/10/2026; las deducidas ya las reetiquetó Gemini
    ("Plantilla", "proceso-explicado"): ("Plantilla", "demostracion"),
    ("Soporte", "TikTok"): ("Soporte", "Reel"),
    ("Soporte", "Vídeo"): ("Soporte", "Reel"),
    ("Soporte", "Serie"): ("Soporte", "Reel"),
    ("Soporte", "Otro"): None,
}


def plantillas():
    return sorted(f[:-3] for f in os.listdir(PLANTILLAS_DIR)
                  if f.endswith(".md") and not f.startswith(("_", "README")))


def listas():
    return {"Tipo de idea": TIPO_IDEA, "Formato": FORMATO, "Plantilla": plantillas(),
            "Palanca": PALANCA, "Soporte": SOPORTE}


def valores(props, campo):
    """Valores actuales de una propiedad, sea select o multi_select."""
    p = props.get(campo) or {}
    if p.get("type") == "multi_select" or "multi_select" in p:
        return [o["name"] for o in (p.get("multi_select") or [])]
    sel = p.get("select")
    return [sel["name"]] if sel else []


def remapear(actuales, finales):
    """{campo: [valores nuevos]} a partir de {campo: [valores viejos]}. Devuelve (nuevo, perdidos)."""
    nuevo = {c: [] for c in CAMPOS}
    perdidos = []
    for campo, vals in actuales.items():
        for v in vals:
            destino = MAPA.get((campo, v), (campo, v))
            if destino is None:
                continue
            c2, v2 = destino
            if v2 in finales.get(c2, []):
                if v2 not in nuevo[c2]:
                    nuevo[c2].append(v2)
            else:
                perdidos.append(f"{campo}:{v}")
    return nuevo, perdidos


def sincronizar_base(label, db, tok, dry):
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    presentes = [c for c in CAMPOS if c in props]
    if not presentes:
        print(f"· {label}: no tiene estas columnas, la salto.")
        return 0
    finales = listas()
    multi = {c: (props[c]["type"] == "multi_select") for c in presentes}

    # 1. filas
    tocadas, perdidos_total = 0, {}
    for pg in na.query(db, tok):
        p = pg["properties"]
        actuales = {c: valores(p, c) for c in presentes}
        if not any(actuales.values()):
            continue
        nuevo, perdidos = remapear(actuales, finales)
        for x in perdidos:
            perdidos_total[x] = perdidos_total.get(x, 0) + 1
        cambios = {}
        for c in presentes:
            if sorted(nuevo[c]) == sorted(actuales[c]):
                continue
            if multi[c]:
                cambios[c] = na.prop_multi(nuevo[c])
            else:
                cambios[c] = na.prop_select(nuevo[c][0]) if nuevo[c] else {"select": None}
        if not cambios:
            continue
        if dry:
            tocadas += 1
            continue
        try:
            na.update_props(pg["id"], tok, cambios)
            tocadas += 1
        except RuntimeError as e:
            sys.stderr.write(f"✗ {label} fila: {e}\n")

    # 2. esquema
    payload = {"properties": {}}
    for c in presentes:
        tipo = props[c]["type"]
        payload["properties"][c] = {tipo: {"options": [{"name": n} for n in finales[c]]}}
    if not dry:
        na._request("PATCH", f"/databases/{db}", tok, payload)
    print(f"{'(dry-run) ' if dry else '✓ '}{label}: {tocadas} filas remapeadas · "
          f"esquema a {sum(len(finales[c]) for c in presentes)} opciones en {len(presentes)} columnas")
    if perdidos_total:
        print(f"   ⚠️ sin equivalencia (se pierden): "
              + ", ".join(f"{k} ×{v}" for k, v in sorted(perdidos_total.items())))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Aplica las listas de ETIQUETAS.md en Notion.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", action="append", default=[],
                    help="Base extra a sincronizar (repetible). P. ej. la de rendimiento.")
    a = ap.parse_args()
    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()
    objetivos = [("Bandeja", cfg["bandeja"]["database_id"])]
    objetivos += [(c["label"], c["database_id"]) for c in cfg["clientes"].values()]
    objetivos += [(f"base {d[:8]}…", d) for d in a.db]
    for label, db in objetivos:
        try:
            sincronizar_base(label, db, tok, a.dry_run)
        except RuntimeError as e:
            sys.stderr.write(f"✗ {label}: {e}\n")
    if a.dry_run:
        print("\n(dry-run: no se ha tocado nada)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
