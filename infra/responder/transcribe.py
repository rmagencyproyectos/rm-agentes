#!/usr/bin/env python3
"""Transcribe un audio a texto con AssemblyAI (español).

Uso:   transcribe.py <ruta_audio>
Requiere ASSEMBLYAI_API_KEY en el entorno. Imprime el texto por stdout.
Códigos de salida: 0 OK · 2 sin clave · 3 error transcripción · 4 timeout · 5 otro.
"""
import json
import os
import sys
import time
import urllib.request

KEY = os.environ.get("ASSEMBLYAI_API_KEY", "").strip()
if not KEY:
    sys.stderr.write("NO_KEY\n")
    sys.exit(2)


def req(url, method="GET", data=None, headers=None):
    r = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read())


def main():
    path = sys.argv[1]
    audio = open(path, "rb").read()
    try:
        up = req("https://api.assemblyai.com/v2/upload", "POST",
                 data=audio, headers={"authorization": KEY})
        tr = req("https://api.assemblyai.com/v2/transcript", "POST",
                 data=json.dumps({"audio_url": up["upload_url"],
                                  "language_code": "es"}).encode(),
                 headers={"authorization": KEY, "content-type": "application/json"})
        tid = tr["id"]
        for _ in range(80):
            st = req(f"https://api.assemblyai.com/v2/transcript/{tid}",
                     headers={"authorization": KEY})
            if st["status"] == "completed":
                sys.stdout.write((st.get("text") or "").strip())
                return 0
            if st["status"] == "error":
                sys.stderr.write("ERR " + str(st.get("error")) + "\n")
                return 3
            time.sleep(3)
        return 4
    except Exception as e:
        sys.stderr.write("EXC " + str(e) + "\n")
        return 5


if __name__ == "__main__":
    sys.exit(main())
