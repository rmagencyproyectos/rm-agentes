#!/usr/bin/env python3
"""Reparte las ideas Aprobadas de la Bandeja a la base del cliente que les toca.

Flujo (una sola dirección): la Bandeja de Ideas RM es la ENTRADA; cuando Gerard aprueba una idea
(Estado = "Aprobada") y le pone Cliente, esta idea tiene que "bajar" a `Contenido <Cliente>`.
Este script hace ese salto:

  Bandeja[Estado=Aprobada, Cliente=X, sin Ficha]  ->  crea fila en Contenido X
      (Resolución=Aprobada, Guion=Coco a guionizar, Producción=Pendiente de grabar)
  ->  marca la Bandeja: Estado=Distribuida + Ficha=<url de la fila creada>

UNA SOLA NOCHE (decisión 28/07): la tarjeta baja ya "Coco a guionizar", así guionizar.py
—que corre justo después en noche.sh— la escribe esa MISMA madrugada. Aprobar en la Bandeja es
el único gate; ya no hay una segunda revisión en la base del cliente antes de guionizar.

Es IDEMPOTENTE: si la fila de la Bandeja ya tiene Ficha, se salta (no duplica). Por eso se puede
correr cada noche sin miedo. Lo lanza el LaunchAgent `com.rmagency.notion-noche` a las 00:45,
antes de guionizar.py.

Uso:  distribuir.py [--dry-run] [--cliente <slug>]
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import datetime
import sys

import etiquetas_idea as ei
import notion_api as na

# La Bandeja permite soportes que las bases de cliente no (TikTok, Otro). Se normalizan.
# (Soporte = Reel/Carrusel/Story; hasta el 22/09/2026 se llamaba "Formato".)
FORMATO_MAP = {"Reel": "Reel", "Carrusel": "Carrusel", "Story": "Story",
               "TikTok": "Reel", "Otro": None}


def bandeja_pendientes(cfg, tok, solo_cliente=None):
    filtro = {"and": [
        {"property": "Estado", "select": {"equals": "Aprobada"}},
        {"property": "Cliente", "select": {"is_not_empty": True}},
    ]}
    filas = na.query(cfg["bandeja"]["database_id"], tok, filtro)
    out = []
    for f in filas:
        p = f["properties"]
        cliente = na.plain(p.get("Cliente"))
        ficha = na.plain(p.get("Ficha"))
        if ficha:  # ya distribuida (idempotencia)
            continue
        if solo_cliente and cliente != solo_cliente:
            continue
        out.append({
            "page_id": f["id"],
            "idea": na.plain(p.get("Idea")),
            "cliente": cliente,
            "tipo": na.plain(p.get("Tipo")),
            "soporte": ei.leer(p, ei.PROP_SOPORTE, cfg["bandeja"]["database_id"], tok),
            "tipo_idea": na.plain(p.get("Tipo de idea")),
            "formato": ei.leer(p, ei.PROP_FORMATO, cfg["bandeja"]["database_id"], tok),
            "autor": na.plain(p.get("Autor")),
            "plantilla": na.plain(p.get("Plantilla")),
            "notas": na.plain(p.get("Notas")),
            "referencia": na.plain(p.get("Referencia")),
        })
    return out


def crear_en_cliente(cfg, tok, item):
    cli = cfg["clientes"].get(item["cliente"])
    if not cli:
        raise RuntimeError(f"Cliente desconocido en config: {item['cliente']}")
    props = {
        "Idea": na.prop_title(item["idea"]),
        # Baja ya aprobada y lista para guionar: guionizar.py la coge esa misma noche (1 noche).
        "Resolución": na.prop_select("Aprobada"),
        "Guion": na.prop_select("Coco a guionizar"),
        "Producción": na.prop_select("Pendiente de grabar"),
    }
    if item["tipo"]:
        props["Tipo"] = na.prop_select(item["tipo"])
    sop = FORMATO_MAP.get(item["soporte"], item["soporte"])
    if sop:
        props["Soporte"] = na.prop_select(sop)
    # Las etiquetas de la idea bajan tal cual: son lo que luego mide el termómetro
    # (etiquetas_idea.py). Si la opción no existe en la base del cliente, Notion la crea.
    for prop, clave in (("Tipo de idea", "tipo_idea"), ("Formato", "formato"), ("Autor", "autor"),
                        ("Plantilla", "plantilla")):
        if item.get(clave):
            props[prop] = na.prop_select(item[clave])
    # La referencia de inspiración y el origen se guardan en Notas (la base de cliente no los tiene
    # como campos propios; el guion los aprovecha si están).
    notas = item["notas"] or ""
    if item["referencia"]:
        notas = (notas + f"\nReferencia: {item['referencia']}").strip()
    if notas:
        props["Notas"] = na.prop_text(notas)
    page = na.create_page(cli["database_id"], tok, ei.traducir(props, cli["database_id"], tok))
    return page.get("url", ""), page.get("id", "")


def main():
    ap = argparse.ArgumentParser(description="Reparte ideas Aprobadas de la Bandeja a los clientes.")
    ap.add_argument("--dry-run", action="store_true", help="No escribe nada, solo lista.")
    ap.add_argument("--cliente", help="Limita a un slug de cliente.")
    a = ap.parse_args()

    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()

    try:
        pendientes = bandeja_pendientes(cfg, tok, a.cliente)
    except RuntimeError as e:
        sys.stderr.write(f"No pude leer la Bandeja: {e}\n")
        return 1

    if not pendientes:
        print("Nada que distribuir.")
        return 0

    hechas = 0
    for it in pendientes:
        etiqueta = f"[{it['cliente']}] {(it['idea'] or '')[:60]}"
        if a.dry_run:
            print(f"(dry-run) distribuiría: {etiqueta}")
            continue
        try:
            url, _ = crear_en_cliente(cfg, tok, it)
            na.update_props(it["page_id"], tok, {
                "Estado": na.prop_select("Distribuida"),
                "Ficha": na.prop_url(url),
            })
            print(f"✓ {etiqueta} -> {url}")
            hechas += 1
        except RuntimeError as e:
            sys.stderr.write(f"✗ {etiqueta}: {e}\n")

    if not a.dry_run:
        print(f"\nDistribuidas {hechas}/{len(pendientes)} · {datetime.datetime.now():%Y-%m-%d %H:%M}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
