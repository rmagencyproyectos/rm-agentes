#!/usr/bin/env python3
"""Sube un vídeo de Google Drive a Metricool y devuelve la URL de media para adjuntarlo a un post.

Receta descubierta y probada el 27/07/2026 (API de Metricool no documentada). Ver la memoria
`metricool-subida-video`. Resumen del flujo:
  1) Descargar el vídeo de Drive con la service account (GOOGLE_SA_JSON, scope drive.readonly).
  2) PUT /v2/media/s3/upload-transactions  (resourceType="planner", part con hash SHA256-base64,
     size = endByte-startByte con endByte EXCLUSIVO) → devuelve presignedUrl + fileUrl.
  3) PUT de los bytes a presignedUrl con headers Content-Type + x-amz-checksum-sha256 (los que
     firma S3; NO mandar Content-MD5).
  4) Usar `fileUrl` en el campo `media` del post del scheduler.

Se ejecuta con /usr/bin/python3 (el único con SSL en este Mac).
"""
import base64
import hashlib
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import warnings

# Silencia los FutureWarning de las libs de Google en /usr/bin/python3 (3.9 EOL): ensucian la
# salida de programar.py sin aportar nada operativo.
warnings.filterwarnings("ignore", category=FutureWarning)

API = "https://app.metricool.com/api"
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def descargar_de_drive(env, drive_id):
    """Devuelve (bytes, nombre, mime) del archivo de Drive usando la service account."""
    sa = env.get("GOOGLE_SA_JSON") or os.environ.get("GOOGLE_SA_JSON")
    if not sa or not os.path.exists(sa):
        raise RuntimeError("Falta GOOGLE_SA_JSON en infra/.env (credencial de Drive).")
    from google.oauth2 import service_account  # import perezoso
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    creds = service_account.Credentials.from_service_account_file(sa, scopes=DRIVE_SCOPES)
    svc = build("drive", "v3", credentials=creds, cache_discovery=False)
    meta = svc.files().get(fileId=drive_id, fields="name,mimeType,size").execute()
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, svc.files().get_media(fileId=drive_id), chunksize=8 * 1024 * 1024)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue(), meta["name"], meta.get("mimeType", "video/mp4")


# Metricool rechaza cualquier parte de más de 100 MiB con
# `InvalidPresignedUploadRequestException: part size exceeds maximum` (medido el 19/08/2026:
# 95 MiB pasa, 101 MiB no). Se trocea por debajo para dejar margen.
MAX_PARTE = 90 * 1024 * 1024


def _sha(b):
    return base64.b64encode(hashlib.sha256(b).digest()).decode()


def subir_a_metricool(env, blog_id, data, filename, content_type):
    """Sube los bytes a Metricool (transacción S3 + PUT) y devuelve la fileUrl para `media`.

    Hasta 90 MiB va en una sola parte (uploadType SIMPLE) y la transacción ya trae la fileUrl.
    Por encima, la API abre una MULTIPART: hay que subir cada parte a su presignedUrl, quedarse
    con el ETag de cada una, y cerrar la transacción con un PATCH al mismo endpoint —
    `{"multipart": {key, bucket, uploadId, parts}}`— que es el que devuelve la fileUrl.
    (Multiparte descubierto el 19/08/2026 al programar Xavi: 4 de sus vídeos pasaban de 100 MiB.)
    """
    tok = env.get("METRICOOL_API_TOKEN")
    uid = env.get("METRICOOL_USER_ID")
    if not tok or not uid:
        raise RuntimeError("Faltan METRICOOL_API_TOKEN / METRICOOL_USER_ID en infra/.env")

    size = len(data)
    q = urllib.parse.urlencode({"userToken": tok, "userId": uid, "blogId": blog_id})
    url_tx = f"{API}/v2/media/s3/upload-transactions?{q}"
    cabeceras = {"Content-Type": "application/json", "X-Mc-Auth": tok,
                 "Accept": "application/json"}

    # 1) Crear la transacción, declarando los tramos en los que se va a subir.
    partes = []
    for inicio in range(0, size, MAX_PARTE):
        trozo = data[inicio:inicio + MAX_PARTE]
        partes.append({"partNumber": len(partes) + 1, "startByte": inicio,
                       "endByte": inicio + len(trozo), "size": len(trozo),
                       "hash": _sha(trozo)})
    body = {"filename": filename, "contentType": content_type,
            "resourceType": "planner", "parts": partes}
    req = urllib.request.Request(url_tx, data=json.dumps(body).encode(), method="PUT",
                                 headers=cabeceras)
    with urllib.request.urlopen(req, timeout=60) as r:
        tx = json.loads(r.read().decode())["data"]

    # 2) Subir cada parte a su URL prefirmada (headers EXACTOS que firma S3).
    subidas = []
    for p in tx["parts"] if tx.get("parts") else [{"partNumber": 1, "startByte": 0,
                                                   "endByte": size,
                                                   "presignedUrl": tx["presignedUrl"]}]:
        trozo = data[p["startByte"]:p["endByte"]]
        sha_b64 = _sha(trozo)
        put = urllib.request.Request(
            p["presignedUrl"], data=trozo, method="PUT",
            headers={"Content-Type": content_type, "x-amz-checksum-sha256": sha_b64},
        )
        with urllib.request.urlopen(put, timeout=1800) as r:
            if r.status not in (200, 204):
                raise RuntimeError(f"S3 PUT parte {p['partNumber']} devolvió {r.status}")
            subidas.append({"partNumber": p["partNumber"],
                            "etag": (r.headers.get("ETag") or "").strip('"'),
                            "checksumSha256": sha_b64})

    # 3) En SIMPLE la fileUrl ya vino con la transacción; en MULTIPART hay que cerrarla.
    if tx.get("fileUrl"):
        return tx["fileUrl"]
    cierre = {"multipart": {"key": tx["key"], "bucket": tx["bucket"],
                            "uploadId": tx["uploadId"], "parts": subidas}}
    req = urllib.request.Request(url_tx, data=json.dumps(cierre).encode(), method="PATCH",
                                 headers=cabeceras)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())["data"]["fileUrl"]


def subir_video_de_drive(env, blog_id, drive_id):
    """Descarga de Drive + sube a Metricool. Devuelve la URL de media lista para el post."""
    data, nombre, mime = descargar_de_drive(env, drive_id)
    if not mime.startswith("video/"):
        mime = "video/mp4"
    return subir_a_metricool(env, blog_id, data, nombre, mime)
