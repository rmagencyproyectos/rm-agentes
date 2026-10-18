#!/usr/bin/env python3
"""Auto-programación nocturna (item 6 del calendario editorial).

Coge las piezas que están **listas para programar** y las deja como **BORRADOR** en
Metricool con el copy de Coco, rellena Notion y avisa a Gerard por WhatsApp + email.
NADA se publica: solo borradores (Gate 3). Gerard da el firme por la mañana en el planner.

**Disparador (una pieza "lista para programar")**:
    Producción = "Editado"  ·  Publicación vacía  ·  "Vídeo final" con URL

**Qué hace por cada pieza** (en orden, saltando días ya ocupados en Metricool):
  1. le asigna el próximo hueco de publicación del cliente (calendario canónico, 15:00),
  2. el copy: se REUTILIZA el `Copy RRSS` que Coco ya escribió al guionizar; solo si está
     vacío (piezas viejas, anteriores al 26/08/2026) lo escribe aquí desde el `copy-brief.md`,
  3. crea el BORRADOR en Metricool (reutiliza `infra/metricool/programar_pieza.py --confirmar`),
  4. escribe en Notion: Publicación = la fecha, Copy RRSS = el copy, "Metricool ID" = id del borrador,
  5. al final, un aviso resumido por WhatsApp + email con el enlace a cada borrador.

Solo Reel/Story (llevan vídeo). Los Carrusel se saltan (necesitan imágenes, no un vídeo).

Se lanza de madrugada desde `noche.sh` (tras guionizar). Interpretador: /usr/bin/python3.

    autoprogramar.py --dry-run          # enseña la cola + huecos, NO llama a Coco ni toca nada
    autoprogramar.py                     # crea borradores + copy + rellena Notion + avisa
    autoprogramar.py --cliente golossa   # solo un cliente
    autoprogramar.py --sin-aviso         # no manda el WhatsApp/email final
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
sys.path.insert(0, os.path.join(HUB, "infra/programacion"))
import etiquetas_idea as ei         # noqa: E402
import notion_api as na            # noqa: E402
import calendario as cal           # noqa: E402  (asignar_slots, fechas_ocupadas, brand_id — calendario canónico)

PROGRAMAR_PIEZA = os.path.join(HUB, "infra/metricool/programar_pieza.py")
NOTIFY = os.path.join(HUB, "infra/notifier/notify.sh")
PYTHON = "/usr/bin/python3"        # el único con SSL en este Mac
MODELO = "claude-sonnet-5"
PRESUPUESTO_USD = "0.20"           # por copy
HORA = "15:00"

# Propiedades (mismas que usa la app y el resto del hub).
PROD, PUB, VID, COPY, MCID, FMT, TIPO, IDEA = (
    "Producción", "Publicación", "Vídeo final", "Copy RRSS", "Metricool ID", "Soporte", "Tipo", "Idea")
# FMT = Reel/Carrusel/Story. En Notion se llama "Soporte" desde el 22/09/2026; "Formato" es
# ahora el formato del contenido (tips, top…) y NO decide el tipo de post en Metricool.


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


def prompt_copy(titulo, fmt, slug, label):
    return (
        f"Eres Coco, la copywriter de RM Agency. Escribe el **copy de redes** (Instagram/TikTok) "
        f"para este {fmt or 'Reel'} de **{label}**.\n\n"
        f"IDEA / TÍTULO DE LA PIEZA: {titulo}\n\n"
        f"=== MARCA Y TONO ===\n{contexto_cliente(slug)}\n\n"
        "Reglas: engancha en la primera línea; 2-5 líneas; termina con una llamada a la acción "
        "natural; incluye 3-6 hashtags relevantes al final; usa emojis con moderación; NADA de "
        "explicaciones ni comillas.\n"
        "Devuelve SOLO el texto del copy, listo para pegar en el post."
    )


def coco_copy(titulo, fmt, slug, label, modelo):
    """Llama a claude -p sin herramientas y devuelve el copy (texto plano). Lanza si falla."""
    proc = subprocess.run(
        ["claude", "-p", "--model", modelo, "--tools", "", "--disable-slash-commands",
         "--no-session-persistence", "--max-budget-usd", PRESUPUESTO_USD, "--output-format", "json"],
        input=prompt_copy(titulo, fmt, slug, label), capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"claude salió {proc.returncode}: {proc.stderr[:300]}")
    d = json.loads(proc.stdout)
    if d.get("is_error") or d.get("subtype") != "success":
        raise RuntimeError(f"claude error: {d.get('subtype')} {str(d.get('result'))[:200]}")
    return (d.get("result") or "").strip().strip('"').strip()


def pendientes(db, tok):
    """Piezas listas para programar: Editado + sin fecha + con Vídeo final."""
    filtro = {"and": [
        {"property": PROD, "select": {"equals": "Editado"}},
        {"property": PUB, "date": {"is_empty": True}},
        {"property": VID, "url": {"is_not_empty": True}},
    ]}
    out = []
    for pg in na.query(db, tok, filtro):
        pr = pg.get("properties", {})
        out.append({
            "page_id": pg["id"],
            "titulo": na.plain(pr.get(IDEA)) or "(sin título)",
            "formato": ei.leer(pr, FMT, db, tok) or "Reel",
            "tipo": na.plain(pr.get(TIPO)) or "",
            "video": na.plain(pr.get(VID)) or "",
            # Copy que ya escribió Coco al guionizar (26/08/2026). Si viene, no se re-genera:
            # ese es el que Gerard ha podido revisar en la ficha, y regenerarlo aquí lo pisaría.
            "copy": na.plain(pr.get(COPY)) or "",
        })
    return out


def crear_borrador(notion_db, fmt, dt_iso, copy, drive_url, titulo):
    """Crea un BORRADOR en Metricool vía programar_pieza.py --confirmar. Devuelve (ok, post_id, out)."""
    payload = {"notionDb": notion_db, "format": fmt, "datetime": dt_iso,
               "copy": copy, "driveUrl": drive_url, "title": titulo}
    proc = subprocess.run([PYTHON, PROGRAMAR_PIEZA, "--confirmar"],
                          input=json.dumps(payload), capture_output=True, text=True, timeout=300)
    try:
        out = json.loads(proc.stdout or "{}")
    except Exception:
        out = {"ok": False, "raw": (proc.stdout or proc.stderr)[:300]}
    res = out.get("result") or out.get("results") or {}
    if isinstance(res, list):
        res = res[0] if res else {}
    post_id = (res.get("data") or {}).get("id") if isinstance(res.get("data"), dict) else res.get("id")
    return bool(out.get("ok")) and bool(post_id), (str(post_id) if post_id else ""), out


def link_metricool(brand_id, post_id):
    return f"https://app.metricool.com/planning/list?blogId={brand_id}&postId={post_id}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cliente", help="Solo este slug (golossa, jesus-mora, …)")
    ap.add_argument("--dry-run", action="store_true", help="Enseña qué haría, sin Coco ni escribir")
    ap.add_argument("--sin-aviso", action="store_true", help="No mandar el WhatsApp/email final")
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--max", type=int, default=0, help="Tope de piezas por cliente (0 = sin tope)")
    a = ap.parse_args()

    tok = na.token()
    cfg = na.load_config()
    hoy = datetime.date.today()
    hechos = []      # borradores creados (para el aviso)
    saltados = []    # (cliente, titulo, motivo)

    for slug, info in cfg.get("clientes", {}).items():
        if a.cliente and slug != a.cliente:
            continue
        db = info.get("database_id")
        label = info.get("label", slug)
        if not db:
            continue
        try:
            cola = pendientes(db, tok)
        except Exception as e:  # noqa: BLE001
            saltados.append((slug, "(consulta)", f"Notion: {e}"))
            continue
        if a.max:
            cola = cola[:a.max]
        # Solo piezas con vídeo (Reel/Story). Carrusel se salta (necesita imágenes).
        listas = [p for p in cola if p["formato"] in ("Reel", "Story")]
        for p in cola:
            if p["formato"] not in ("Reel", "Story"):
                saltados.append((slug, p["titulo"], f"formato {p['formato']} (necesita imágenes)"))
        if not listas:
            continue

        ocupadas = set() if a.dry_run else cal.fechas_ocupadas(slug, hoy, hoy + datetime.timedelta(days=180))
        fechas = cal.asignar_slots(slug, hoy, len(listas), ocupadas)
        brand = cal.brand_id(slug)

        for pieza, fecha in zip(listas, fechas):
            dt_iso = f"{fecha.isoformat()}T{HORA}:00"
            if a.dry_run:
                print(f"[{slug}] {fecha:%a %d/%m} {HORA} · {pieza['formato']} · {pieza['titulo']!r}  → borrador (dry-run)")
                continue
            # 1) Copy: el de la ficha manda; solo se pide a Coco si no hay ninguno.
            copy = pieza["copy"]
            if not copy:
                try:
                    copy = coco_copy(pieza["titulo"], pieza["formato"], slug, label, a.modelo)
                except Exception as e:  # noqa: BLE001
                    saltados.append((slug, pieza["titulo"], f"copy Coco: {e}"))
                    continue
            # 2) Borrador en Metricool
            ok, post_id, out = crear_borrador(db, pieza["formato"], dt_iso, copy, pieza["video"], pieza["titulo"])
            if not ok:
                saltados.append((slug, pieza["titulo"], f"Metricool: {out.get('error') or out.get('raw') or 'sin id'}"))
                continue
            # 3) Rellenar Notion (fecha + copy + Metricool ID). Producción sigue Editado, pero ya con fecha
            #    → sale de la cola y no se re-programa la próxima noche.
            try:
                na.update_props(pieza["page_id"], tok, {
                    PROD: na.prop_select("Borrador"),
                    PUB: na.prop_date(dt_iso),
                    COPY: na.prop_text(copy),
                    MCID: na.prop_text(post_id),
                })
            except Exception as e:  # noqa: BLE001
                saltados.append((slug, pieza["titulo"], f"Notion update (borrador {post_id} SÍ creado): {e}"))
            hechos.append({"slug": slug, "label": label, "titulo": pieza["titulo"],
                           "fecha": fecha.isoformat(), "post_id": post_id,
                           "link": link_metricool(brand, post_id) if brand else ""})

    # Resumen
    print(f"\n== autoprogramar {'(DRY-RUN)' if a.dry_run else ''}: {len(hechos)} borrador(es), {len(saltados)} saltado(s) ==")
    for h in hechos:
        print(f"  ✓ {h['label']}: {h['fecha']} · {h['titulo']}  {h['link']}")
    for s in saltados:
        print(f"  · saltado {s[0]}/{s[1]!r}: {s[2]}")

    # Aviso a Gerard (WhatsApp + email) — solo si se crearon borradores de verdad.
    if hechos and not a.dry_run and not a.sin_aviso:
        porcli = {}
        for h in hechos:
            porcli.setdefault(h["label"], []).append(h)
        lineas = [f"🌙 *Auto-programación* — {len(hechos)} borrador(es) listos para tu OK:\n"]
        for label, hs in porcli.items():
            lineas.append(f"*{label}*")
            for h in hs:
                d = datetime.date.fromisoformat(h["fecha"])
                lineas.append(f"  · {cal.cob.DIAS_ES[d.weekday()]} {d:%d/%m} — {h['titulo']}")
        lineas.append("\nRevísalos en Metricool y dales al firme cuando quieras.")
        msg = "\n".join(lineas)
        try:
            # "wa+email": los dos canales, no en cascada (antes solo llegaba el WhatsApp aunque
            # este aviso siempre se documentó como WhatsApp + email).
            subprocess.run([NOTIFY, msg, "LOTE_LISTO", "normal", "wa+email",
                            "[RM] Borradores listos en Metricool"], timeout=120)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ no pude avisar: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
