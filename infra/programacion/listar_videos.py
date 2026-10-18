#!/usr/bin/env python3
"""Lista los vídeos de un cliente en Google Drive, ordenados por el número del nombre.

Los vídeos viven en `Drive de rmagency.proyectos / <CLIENTE> / <MES> / N_...mp4` (ver
`config/drive-carpetas.json`). Este script recorre la carpeta del cliente, junta los vídeos y
los ordena por el número inicial del nombre (1_JMORA_, 2_JMORA_...), que es el orden de
publicación por defecto. Gerard puede reordenarlos luego; este script solo propone.

Requisitos (prerequisito de Gerard, una vez):
  - pip para /usr/bin/python3:  google-api-python-client  google-auth
  - una service account de Google con la API de Drive, su JSON de credenciales, y las carpetas
    de cliente COMPARTIDAS con el email de la service account (lectura).
  - en infra/.env:  GOOGLE_SA_JSON=/ruta/al/service-account.json

Uso:
  listar_videos.py --cliente jesus-mora            -> JSON [{orden, archivo, titulo, id, url}]
  listar_videos.py --cliente jesus-mora --titulos  -> solo los títulos sugeridos, uno por línea
                                                      (para encadenar con calendario.py)
Salida:
  0  ok
  2  falta configurar (librerías, credencial, o carpeta del cliente sin id)  -> Winy avisa
  1  otro error
"""
import argparse
import json
import os
import re
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
CARPETAS = os.path.join(HUB, "config/drive-carpetas.json")
VIDEO_MIMES = ("video/",)
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def load_env():
    env = {}
    try:
        with open(os.path.join(HUB, "infra/.env")) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v
    except FileNotFoundError:
        pass
    return env


def carpeta_cliente(cliente):
    with open(CARPETAS, encoding="utf-8") as f:
        data = json.load(f)
    return (data.get("carpetas") or {}).get(cliente)


def orden_key(nombre):
    m = re.match(r"\s*(\d+)", nombre)
    return (0, int(m.group(1)), nombre.lower()) if m else (1, 0, nombre.lower())


def titulo_sugerido(nombre):
    stem = os.path.splitext(nombre)[0]
    stem = re.sub(r"^\s*\d+\s*[_\-.]\s*", "", stem)      # quita "12_"
    stem = re.sub(r"^[A-Za-z]{2,10}[_\-]", "", stem)     # quita prefijo de cliente (JMORA_, JM_)
    return stem.replace("_", " ").replace("-", " ").strip() or stem


def construir_servicio(env):
    """Devuelve el cliente de Drive o None si faltan librerías/credencial (exit 2)."""
    sa = env.get("GOOGLE_SA_JSON") or os.environ.get("GOOGLE_SA_JSON")
    if not sa or not os.path.exists(sa):
        sys.stderr.write("Falta GOOGLE_SA_JSON en infra/.env (credencial de Drive sin configurar).\n")
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        sys.stderr.write("Faltan librerías: pip install google-api-python-client google-auth\n")
        return None
    creds = service_account.Credentials.from_service_account_file(sa, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def listar_recursivo(service, carpeta, profundidad=3):
    """Vídeos bajo `carpeta` (bajando por subcarpetas de mes hasta `profundidad` niveles)."""
    videos, pendientes = [], [(carpeta, profundidad)]
    while pendientes:
        fid, prof = pendientes.pop()
        page = None
        while True:
            resp = service.files().list(
                q=f"'{fid}' in parents and trashed=false",
                fields="nextPageToken, files(id,name,mimeType)",
                pageSize=1000, pageToken=page,
                includeItemsFromAllDrives=True, supportsAllDrives=True,
            ).execute()
            for f in resp.get("files", []):
                mime = f.get("mimeType", "")
                if mime == "application/vnd.google-apps.folder":
                    if prof > 0:
                        pendientes.append((f["id"], prof - 1))
                elif mime.startswith(VIDEO_MIMES):
                    videos.append(f)
            page = resp.get("nextPageToken")
            if not page:
                break
    return videos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cliente", required=True)
    p.add_argument("--titulos", action="store_true", help="Imprime solo títulos sugeridos")
    a = p.parse_args()

    carpeta = carpeta_cliente(a.cliente)
    if not carpeta:
        sys.stderr.write(f"El cliente '{a.cliente}' no tiene carpeta en config/drive-carpetas.json.\n")
        return 2

    env = load_env()
    service = construir_servicio(env)
    if service is None:
        return 2

    try:
        videos = listar_recursivo(service, carpeta)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"No pude leer Drive: {e}\n")
        return 1

    videos.sort(key=lambda f: orden_key(f["name"]))
    items = [{
        "orden": i + 1,
        "archivo": v["name"],
        "titulo": titulo_sugerido(v["name"]),
        "id": v["id"],
        "url": f"https://drive.google.com/file/d/{v['id']}/view",
    } for i, v in enumerate(videos)]

    if a.titulos:
        sys.stdout.write("\n".join(it["titulo"] for it in items) + ("\n" if items else ""))
    else:
        sys.stdout.write(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
