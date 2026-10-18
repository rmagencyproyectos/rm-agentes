#!/usr/bin/env python3
"""El puente entre lo que escribió Coco y lo que analiza el Analista.

El problema que resuelve: el Analista trabaja con el PDF bruto de Metricool, que trae vistas,
alcance y el texto del post — pero **no sabe con qué plantilla ni con qué metodología se hizo
cada pieza**. Sin eso solo puede decir "este vídeo funcionó", que es justo lo que lleva meses
sin enseñar nada. Con eso puede decir "las demostraciones funcionan y los talking-head no".

Este script recorre las 6 bases de Notion y escribe, por cliente, una tabla legible de cada
pieza **ya publicada o programada** con su clasificación completa: Tipo · Plantilla ·
Metodología · Palanca · motivo de compartición · fecha. Y le pega encima lo que Coco dejó en
`ciclos/*/  <cliente>/hipotesis.json` (apuesta, porqué, etiquetas), que vive en disco y no en
Notion.

Sale a `memoria/clasificacion/<cliente>.md`. Además deja `memoria/clasificacion/_piezas/<cliente>.json`
(dato de máquina, no se lee a mano): cada pieza publicada con su fecha y TODAS sus etiquetas
(Plantilla, Formato, Tipo de idea, Autor…). Es de donde mide el termómetro (`--ideas`,
`--formatos`, `--autores`, `--plantillas`) cruzando por fecha con Metricool. Se hizo así el 22/09/2026
porque los títulos de `hipotesis.json` y los de Notion no casaban nunca (0 de 22 publicadas):
medir desde Notion es lo único que ve TODAS las piezas que han salido. **Un solo archivo por cliente**, para que el
Analista lo lea entero sin romper su presupuesto de lectura (ver `agentes/analista.md` §6).

Uso:  clasificacion.py [--cliente <slug>] [--stdout]
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import datetime
import glob
import json
import os
import sys

import etiquetas_idea as ei
import notion_api as na

HUB = na.HUB
DEST = os.path.join(HUB, "memoria/clasificacion")
DEST_PIEZAS = os.path.join(DEST, "_piezas")
CICLOS = os.path.join(HUB, "ciclos")


def hipotesis_del_cliente(slug):
    """{titulo: {apuesta, porque, etiquetas, resultado}} de todas las tandas del cliente."""
    fuera = {}
    for ruta in sorted(glob.glob(os.path.join(CICLOS, "*", slug, "hipotesis.json"))):
        try:
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, ValueError):
            continue
        for p in datos.get("piezas", []):
            if p.get("titulo"):
                fuera[p["titulo"].strip()] = p
    return fuera


def filas_del_cliente(cfg, tok, slug):
    """Piezas que ya salieron o van a salir: son las únicas que el Analista puede cruzar."""
    cli = cfg["clientes"][slug]
    out = []
    for f in na.query(cli["database_id"], tok):
        p = f["properties"]
        prod = na.plain(p.get("Producción"))
        fecha = na.plain(p.get("Publicación"))
        # Sin fecha y sin publicar, la pieza aún no existe para el análisis.
        if not fecha and prod not in ("Programado", "Publicado"):
            continue
        out.append({
            "idea": (na.plain(p.get("Idea")) or "").strip(),
            "fecha": (fecha or "")[:10],
            "tipo": na.plain(p.get("Tipo")) or "",
            "plantilla": na.plain(p.get("Plantilla")) or "",
            "metodologia": na.plain(p.get("Metodologia")) or "",
            "palanca": ", ".join(na.plain(p.get("Palanca")) or []),
            "soporte": ei.leer(p, ei.PROP_SOPORTE, cli["database_id"], tok) or "",
            "tipo_idea": na.plain(p.get(ei.PROP_TIPO)) or "",
            "formato": ei.leer(p, ei.PROP_FORMATO, cli["database_id"], tok) or "",
            "autor": na.plain(p.get(ei.PROP_AUTOR)) or "",
            "produccion": prod or "",
        })
    out.sort(key=lambda r: r["fecha"] or "9999", reverse=True)
    return out


def render(slug, label, filas, hip):
    hoy = f"{datetime.datetime.now():%Y-%m-%d %H:%M}"
    L = [f"# 🏷️ Clasificación de contenido — {label} ({slug})", "",
         f"> Con qué se hizo cada pieza. Generado por `infra/notion/clasificacion.py` · {hoy}",
         "",
         "**Para qué sirve**: cruza esto con el ranking del bruto de Metricool. El bruto dice",
         "qué vídeo funcionó; esta tabla dice **qué tenía ese vídeo**. Sin cruzarlas, el",
         "análisis solo puede describir; cruzándolas, puede explicar.", ""]
    if not filas:
        L += ["*(Todavía no hay piezas publicadas o programadas con clasificación.)*", "",
              "Las piezas anteriores al 14/08/2026 no llevan Plantilla ni Metodología: se",
              "guionizaron antes de que existieran y **no se puede reconstruir**. Para esas,",
              "clasifica a ojo desde el texto del post y dilo explícitamente en el deck.", ""]
        return "\n".join(L)

    L += ["## Piezas", "",
          "| Fecha | Pieza | Autor | Tipo | Tipo de idea | Formato | Plantilla | Metodología | Palanca | Soporte |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    sin_clasificar = 0
    for r in filas:
        if not r["plantilla"]:
            sin_clasificar += 1
        L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            r["fecha"] or "—", r["idea"][:52].replace("|", "/"), r["autor"] or "—",
            r["tipo"] or "—", r["tipo_idea"] or "—", r["formato"] or "—",
            r["plantilla"] or "⚠️ sin clasificar", r["metodologia"] or "—",
            r["palanca"] or "—", r["soporte"] or "—"))
    L.append("")

    if sin_clasificar:
        L += [f"⚠️ **{sin_clasificar} de {len(filas)} piezas sin plantilla.** Son anteriores al "
              "14/08/2026. No las mezcles con las clasificadas al sacar conclusiones: una "
              "media hecha sobre piezas sin etiquetar no dice nada.", ""]

    # Lo que Coco apostó por cada pieza (vive en hipotesis.json, no en Notion).
    apuestas = [(r, hip[r["idea"]]) for r in filas if r["idea"] in hip]
    if apuestas:
        L += ["## Qué se apostaba en cada una", "",
              "Escrito **antes** de publicar. Es lo que convierte un número en un aprendizaje.",
              ""]
        for r, p in apuestas:
            L.append(f"### {r['idea'][:70]}")
            L.append(f"- **Plantilla**: {r['plantilla'] or '—'}"
                     + (f" · **Metodología**: {r['metodologia']}" if r["metodologia"] else ""))
            if p.get("apuesta"):
                L.append(f"- **Apuesta**: {p['apuesta']}")
            if p.get("porque"):
                L.append(f"- **Por qué**: {p['porque']}")
            if p.get("etiquetas"):
                L.append(f"- **Etiquetas**: {', '.join(p['etiquetas'])}")
            if p.get("compartible"):
                L.append(f"- **Se comparte por**: {p['compartible']}")
            res = p.get("resultado") or {}
            if res.get("ratio"):
                L.append(f"- **Resultado medido**: x{res['ratio']} sobre la mediana del cliente")
            L.append("")

    L += ["---", "",
          "## Cómo usarlo en el deck", "",
          "1. Coge el **top y el bottom** del ranking del bruto.",
          "2. Búscalos en la tabla y mira **qué plantilla y qué metodología** tenían.",
          "3. Si una plantilla aparece repetida arriba (o abajo), **eso es el patrón** — y ya",
          "   no es una impresión, es una clasificación.",
          "4. Una plantilla con **una sola pieza** no concluye nada. Dilo en vez de callarlo.",
          "5. Lo que salga va a `memoria/aprendizajes/registro.md`, que es de donde Oli saca",
          "   las ideas del mes siguiente.", ""]
    return "\n".join(L)


def guardar_piezas(slug, filas):
    """Snapshot de máquina para el termómetro: solo lo que ya tiene fecha de publicación."""
    os.makedirs(DEST_PIEZAS, exist_ok=True)
    piezas = [{"titulo": r["idea"], "publicado": r["fecha"], "tipo": r["tipo"],
               "plantilla": r["plantilla"], "metodologia": r["metodologia"],
               "soporte": r["soporte"], "tipo_idea": r["tipo_idea"],
               "formato": r["formato"], "autor": r["autor"], "produccion": r["produccion"]}
              for r in filas if r["fecha"]]
    with open(os.path.join(DEST_PIEZAS, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump({"cliente": slug, "generado": f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
                   "piezas": piezas}, f, ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser(description="Tabla de clasificación de contenido por cliente.")
    ap.add_argument("--cliente", help="Limita a un slug.")
    ap.add_argument("--stdout", action="store_true", help="Imprime, no escribe archivos.")
    a = ap.parse_args()

    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()
    os.makedirs(DEST, exist_ok=True)

    fallos = 0
    for slug, cli in cfg["clientes"].items():
        if a.cliente and slug != a.cliente:
            continue
        try:
            filas = filas_del_cliente(cfg, tok, slug)
        except RuntimeError as e:
            sys.stderr.write(f"✗ {cli['label']}: {e}\n")
            fallos += 1
            continue
        texto = render(slug, cli["label"], filas, hipotesis_del_cliente(slug))
        if a.stdout:
            print(texto)
        else:
            with open(os.path.join(DEST, f"{slug}.md"), "w", encoding="utf-8") as f:
                f.write(texto + "\n")
            guardar_piezas(slug, filas)
            con = sum(1 for r in filas if r["plantilla"])
            print(f"✓ {cli['label']}: {len(filas)} piezas ({con} clasificadas)")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
