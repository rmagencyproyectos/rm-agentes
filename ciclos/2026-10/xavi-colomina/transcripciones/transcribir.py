#!/usr/bin/env python3
"""Transcribe vídeos ya montados con AssemblyAI (acepta el mp4 directo, sin ffmpeg).

Se usa para poder escribir el copy de piezas cuyo nombre de archivo no dice de qué van
(los 'Tanda 3-N' de Xavi). Guarda cada transcripción en un .txt al lado, y las cachea:
si el .txt ya existe, no vuelve a gastar API.

Uso: transcribir.py <fichero.mp4> [...]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
API = "https://api.assemblyai.com/v2"
CACHE = os.path.dirname(os.path.abspath(__file__))


def key():
    with open(os.path.join(HUB, "infra/.env")) as f:
        for line in f:
            if line.startswith("ASSEMBLYAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("Falta ASSEMBLYAI_API_KEY")


def subir(path, tok):
    with open(path, "rb") as f:
        req = urllib.request.Request(
            f"{API}/upload", data=f.read(),
            headers={"authorization": tok, "content-type": "application/octet-stream"},
            method="POST")
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())["upload_url"]


def transcribir(url, tok):
    req = urllib.request.Request(
        f"{API}/transcript",
        data=json.dumps({"audio_url": url, "language_code": "es"}).encode(),
        headers={"authorization": tok, "content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        tid = json.loads(r.read())["id"]
    while True:
        req = urllib.request.Request(f"{API}/transcript/{tid}", headers={"authorization": tok})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        if d["status"] == "completed":
            return d.get("text") or ""
        if d["status"] == "error":
            raise RuntimeError(d.get("error"))
        time.sleep(4)


def main(paths):
    os.makedirs(CACHE, exist_ok=True)
    tok = key()
    for p in paths:
        nombre = os.path.splitext(os.path.basename(p))[0]
        destino = os.path.join(CACHE, nombre + ".txt")
        if os.path.exists(destino):
            print(f"= {nombre} (cache)")
            continue
        if not os.path.exists(p):
            print(f"! {nombre} — no existe: {p}")
            continue
        mb = os.path.getsize(p) / 1e6
        print(f"↑ {nombre} ({mb:.0f} MB)...", flush=True)
        try:
            texto = transcribir(subir(p, tok), tok)
        except Exception as e:  # noqa: BLE001
            print(f"! {nombre} — {e}")
            continue
        open(destino, "w", encoding="utf-8").write(texto)
        print(f"✓ {nombre} — {len(texto)} car.\n   {texto[:200]}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
