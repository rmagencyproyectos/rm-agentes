#!/usr/bin/env python3
"""Añade una idea de contenido a la Bandeja de Ideas RM (Notion).

La usa Winy (carril 2) cuando Gerard le pasa una idea o un link de referencia. La idea entra
SIEMPRE en la bandeja central con estado "pendiente de grabar"; desde ahí se distribuye a la
base del cliente (fase posterior).

Sigue el patrón de los scripts de `infra/metricool/`: urllib puro, lee `infra/.env`, pensado
para `/usr/bin/python3` (el 3.9 con certificados SSL; el 3.12 de este Mac falla contra HTTPS).

Requiere en `infra/.env`:
  NOTION_API_TOKEN   token de una internal integration de Notion (secret_...)
  NOTION_DB_BANDEJA  id de la base "Bandeja de Ideas RM" (opcional; hay uno por defecto)
La integración tiene que estar COMPARTIDA con la base (en Notion: ··· → Connections → añadirla).

La idea entra con Estado "Nueva". Desde la Bandeja, Gerard la aprueba (Estado "Aprobada") y
distribuir.py la baja a la base del cliente; el guion, gancho y CTA se rellenan YA en la base del
cliente (los escribe Coco), no aquí.

Uso:
  idea_add.py --idea "<texto>" [--cliente <slug>] [--tipo Viral|Marca]
              [--formato Reel|TikTok|Story|Carrusel|Otro] [--origen "<de dónde salió>"]
              [--referencia <url>] [--notas "..."] [--estado Nueva|Aprobada|Distribuida|Descartada]

Salida:
  0  idea creada (imprime la URL de la página)
  2  falta NOTION_API_TOKEN (aún sin configurar)   -> Winy avisa a Gerard
  1  cualquier otro error (imprime el motivo en stderr)
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
# Base "Bandeja de Ideas RM" creada el 26/07/2026. Se puede sobreescribir con NOTION_DB_BANDEJA.
DB_BANDEJA_DEFECTO = "1a033425-f195-46ed-bccd-b29b2e6163bb"
NOTION_API = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

CLIENTES = {"golossa", "midtown", "jesus-mora", "msm", "newmos", "xavi-colomina",
            "algoritmo", "rm-agency"}
FORMATOS = {"Reel", "TikTok", "Story", "Carrusel", "Otro"}
TIPOS = {"Viral", "Marca"}
ESTADOS = {"Nueva", "Aprobada", "Distribuida", "Descartada"}


def load_env():
    env = {}
    ruta = os.path.join(HUB, "infra/.env")
    try:
        with open(ruta) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v
    except FileNotFoundError:
        pass
    return env


def _texto(valor):
    return {"rich_text": [{"text": {"content": valor[:1900]}}]}


def construir_propiedades(a):
    props = {
        "Idea": {"title": [{"text": {"content": a.idea[:1900]}}]},
        "Estado": {"select": {"name": a.estado}},
        "Fecha": {"date": {"start": datetime.date.today().isoformat()}},
    }
    if a.cliente:
        props["Cliente"] = {"select": {"name": a.cliente}}
    if a.tipo:
        props["Tipo"] = {"select": {"name": a.tipo}}
    if a.formato:
        props["Formato"] = {"select": {"name": a.formato}}
    if a.origen:
        props["Origen"] = _texto(a.origen)
    if a.referencia:
        props["Referencia"] = {"url": a.referencia}
    if a.notas:
        props["Notas"] = _texto(a.notas)
    return props


def desde_json(ruta):
    """Construye el Namespace de argumentos a partir de un JSON de la bandeja de salida (cola)."""
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    cli = d.get("cliente")
    fmt = d.get("formato")
    tipo = d.get("tipo")
    est = d.get("estado") or "Nueva"
    return argparse.Namespace(
        idea=d.get("idea"),
        cliente=cli if cli in CLIENTES else None,
        tipo=tipo if tipo in TIPOS else None,
        formato=fmt if fmt in FORMATOS else None,
        origen=d.get("origen"),
        referencia=d.get("referencia"),
        notas=d.get("notas"),
        estado=est if est in ESTADOS else "Nueva",
        from_json=ruta,
    )


def main():
    p = argparse.ArgumentParser(description="Añade una idea a la Bandeja de Ideas RM (Notion).")
    p.add_argument("--idea")
    p.add_argument("--cliente", choices=sorted(CLIENTES))
    p.add_argument("--tipo", choices=sorted(TIPOS))
    p.add_argument("--formato", choices=sorted(FORMATOS))
    p.add_argument("--origen")
    p.add_argument("--referencia")
    p.add_argument("--notas")
    p.add_argument("--estado", choices=sorted(ESTADOS), default="Nueva")
    p.add_argument("--from-json", dest="from_json",
                   help="Lee los campos de un JSON (bandeja de salida de Winy).")
    a = p.parse_args()
    if a.from_json:
        a = desde_json(a.from_json)
    if not a.idea:
        sys.stderr.write("Falta --idea (o un JSON con campo 'idea').\n")
        return 1

    env = load_env()
    token = env.get("NOTION_API_TOKEN") or os.environ.get("NOTION_API_TOKEN")
    if not token:
        sys.stderr.write("Falta NOTION_API_TOKEN en infra/.env (Notion aún sin configurar).\n")
        return 2
    db = env.get("NOTION_DB_BANDEJA") or os.environ.get("NOTION_DB_BANDEJA") or DB_BANDEJA_DEFECTO

    payload = {"parent": {"database_id": db}, "properties": construir_propiedades(a)}
    req = urllib.request.Request(
        NOTION_API,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        sys.stdout.write(data.get("url", "(creada)"))
        return 0
    except urllib.error.HTTPError as e:
        detalle = e.read().decode(errors="replace")[:500]
        sys.stderr.write(f"Notion respondió {e.code}: {detalle}\n")
        return 1
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"No pude crear la idea: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
