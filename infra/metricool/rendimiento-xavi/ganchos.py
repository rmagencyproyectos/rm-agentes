#!/usr/bin/env python3
"""Rellena «Gancho hablado (0-5 s)» y «Transcripción» en la base de rendimiento de Xavi.

Para cada vídeo PUBLICADO del planner que aún no tenga gancho, manda a AssemblyAI el mp4 que
guarda Metricool (por URL, sin descargar nada) y escribe en Notion:
  - Gancho hablado: lo que se oye en los primeros ~5 s, alargado hasta cerrar la frase
    (máx. 8 s). Es lo que dice Xavi, NO el titular en pantalla.
  - Transcripción: el texto completo.
Cachea cada transcripción en analitica/transcripciones/<metricool_id>.json: si existe, no
vuelve a gastar API. Coste: céntimos por vídeo.

Uso:  python3 analitica/ganchos.py
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metricool_a_notion as m  # noqa: E402  (reutiliza credenciales y la API de Metricool)

na = m.na
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcripciones")
AAI = "https://api.assemblyai.com/v2"


def aai_key():
    return m.E["ASSEMBLYAI_API_KEY"]


def transcribir(url):
    k = aai_key()
    req = urllib.request.Request(f"{AAI}/transcript", method="POST",
                                 data=json.dumps({"audio_url": url, "language_code": "es"}).encode(),
                                 headers={"authorization": k, "content-type": "application/json"})
    tid = json.loads(urllib.request.urlopen(req, timeout=60).read())["id"]
    while True:
        r = urllib.request.Request(f"{AAI}/transcript/{tid}", headers={"authorization": k})
        d = json.loads(urllib.request.urlopen(r, timeout=60).read())
        if d["status"] == "completed":
            return d
        if d["status"] == "error":
            raise RuntimeError(d.get("error"))
        time.sleep(4)


def gancho(words):
    """Palabras que empiezan antes de 5 s; si la frase sigue, hasta cerrarla (máx. 8 s)."""
    out = []
    for w in words:
        if w["start"] >= 8000:
            break
        if w["start"] >= 5000 and out and out[-1]["text"][-1:] in ".?!":
            break
        out.append(w)
    return " ".join(w["text"] for w in out)


def main():
    os.makedirs(CACHE, exist_ok=True)
    tok = na.token()
    filas = na.query(m.DB, tok, {"and": [{"property": "Estado", "select": {"equals": "Publicado"}},
                                         {"property": "Gancho hablado (0-5 s)", "rich_text": {"is_empty": True}},
                                         {"property": "Metricool ID", "rich_text": {"is_not_empty": True}}]})
    planner = {str(p["id"]): p for p in m.mc("/v2/scheduler/posts", start=m.DESDE + "T00:00:00",
                                              end="2027-01-31T23:59:59", extendedRange="true")["data"]}
    print(f"{len(filas)} vídeos publicados sin gancho")
    for f in filas:
        mid = m.plano(f["properties"]["Metricool ID"])
        titulo = m.plano(f["properties"]["Pieza"])[:60]
        media = ((planner.get(mid) or {}).get("media") or [None])[0]
        if not media:
            print(f"! {titulo} — sin vídeo en el planner")
            continue
        ruta = os.path.join(CACHE, mid + ".json")
        if os.path.exists(ruta):
            d = json.load(open(ruta))
        else:
            try:
                d = transcribir(media)
            except Exception as e:  # noqa: BLE001
                print(f"! {titulo} — {e}")
                continue
            json.dump({"text": d.get("text") or "", "words": d.get("words") or []},
                      open(ruta, "w"), ensure_ascii=False)
        g = gancho(d.get("words") or []) or "(sin voz en los primeros segundos)"
        na.update_props(f["id"], tok, {"Gancho hablado (0-5 s)": {"rich_text": m.rt(g)},
                                      "Transcripción": {"rich_text": m.rt(d.get("text") or "")}})
        print(f"✓ {titulo}\n    «{g}»")


if __name__ == "__main__":
    main()
