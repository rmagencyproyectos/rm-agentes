#!/usr/bin/env python3
"""Helper compartido para hablar con la API de Notion (urllib puro, /usr/bin/python3).

Extraído de idea_add.py el 28/07/2026 cuando aparecieron distribuir.py y guionizar.py y los tres
necesitaban lo mismo: leer el token de infra/.env, lanzar peticiones con un reintento, consultar
una base, y crear/actualizar páginas. Sin dependencias externas (el 3.12 de este Mac falla contra
HTTPS; se corre con /usr/bin/python3, el 3.9 con SSL).

No es un CLI: se importa. `load_config()` devuelve el mapa de config/notion-bases.json.
"""
import json
import os
import time
import urllib.error
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"


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


def token():
    env = load_env()
    tok = env.get("NOTION_API_TOKEN") or os.environ.get("NOTION_API_TOKEN")
    if not tok:
        raise RuntimeError("Falta NOTION_API_TOKEN en infra/.env")
    return tok


def load_config():
    with open(os.path.join(HUB, "config/notion-bases.json"), encoding="utf-8") as f:
        return json.load(f)


def _request(method, path, tok, payload=None):
    """Una petición a la API con UN reintento ante error de red o 429/5xx."""
    url = API + path
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    ultimo = None
    for intento in range(2):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                cuerpo = resp.read().decode()
                return json.loads(cuerpo) if cuerpo else {}
        except urllib.error.HTTPError as e:
            detalle = e.read().decode(errors="replace")[:500]
            ultimo = RuntimeError(f"Notion {method} {path} -> {e.code}: {detalle}")
            if e.code in (429, 500, 502, 503) and intento == 0:
                time.sleep(2)
                continue
            raise ultimo
        except Exception as e:  # noqa: BLE001 (red)
            ultimo = RuntimeError(f"Notion {method} {path} -> {e}")
            if intento == 0:
                time.sleep(2)
                continue
            raise ultimo
    raise ultimo


def query(database_id, tok, filtro=None, page_size=100):
    """Devuelve la lista de páginas (results) de una base, aplicando `filtro` (dict) si se da.

    Pagina hasta agotar (has_more). `filtro` sigue el formato de la API de Notion, p.ej.
    {"property": "Guion", "select": {"equals": "Coco a guionizar"}}.
    """
    paginas, cursor = [], None
    while True:
        payload = {"page_size": page_size}
        if filtro:
            payload["filter"] = filtro
        if cursor:
            payload["start_cursor"] = cursor
        data = _request("POST", f"/databases/{database_id}/query", tok, payload)
        paginas.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return paginas


def create_page(database_id, tok, properties, children=None):
    payload = {"parent": {"database_id": database_id}, "properties": properties}
    if children:
        payload["children"] = children
    return _request("POST", "/pages", tok, payload)


def update_props(page_id, tok, properties):
    return _request("PATCH", f"/pages/{page_id}", tok, {"properties": properties})


def append_blocks(page_id, tok, children):
    """Añade bloques al final de una página. Notion limita a 100 bloques por llamada."""
    for i in range(0, len(children), 100):
        _request("PATCH", f"/blocks/{page_id}/children", tok, {"children": children[i:i + 100]})


def list_blocks(page_id, tok):
    """Bloques hijos de una página, en orden. Pagina hasta agotar."""
    bloques, cursor = [], None
    while True:
        sufijo = f"?start_cursor={cursor}" if cursor else ""
        data = _request("GET", f"/blocks/{page_id}/children{sufijo}", tok)
        bloques.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return bloques


def delete_block(block_id, tok):
    """Archiva un bloque (la API de Notion no borra: archiva, y deja de mostrarse)."""
    return _request("DELETE", f"/blocks/{block_id}", tok)


def texto_de_bloque(bloque):
    """Texto plano de un bloque, sea del tipo que sea. Vacío si no tiene."""
    tipo = bloque.get("type") or ""
    cuerpo = bloque.get(tipo) or {}
    return "".join(x.get("plain_text", "") for x in (cuerpo.get("rich_text") or []))


# ---- Helpers de construcción de propiedades (los mismos tipos en todas las bases) ----

def prop_title(texto):
    return {"title": [{"text": {"content": (texto or "")[:1900]}}]}


def prop_text(texto):
    return {"rich_text": [{"text": {"content": (texto or "")[:1900]}}]}


def prop_select(nombre):
    return {"select": {"name": nombre}} if nombre else {"select": None}


def prop_multi(nombres):
    return {"multi_select": [{"name": n} for n in (nombres or [])]}


def prop_url(u):
    return {"url": u or None}


def prop_date(iso):
    return {"date": {"start": iso}} if iso else {"date": None}


def plain(prop):
    """Extrae el texto/valor plano de una propiedad devuelta por la API (para leer)."""
    if prop is None:
        return None
    t = prop.get("type")
    if t == "title":
        return "".join(x.get("plain_text", "") for x in prop.get("title", []))
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))
    if t == "select":
        return (prop.get("select") or {}).get("name")
    if t == "multi_select":
        return [x.get("name") for x in prop.get("multi_select", [])]
    if t == "url":
        return prop.get("url")
    if t == "date":
        return (prop.get("date") or {}).get("start")
    if t == "checkbox":
        return prop.get("checkbox")
    return None
