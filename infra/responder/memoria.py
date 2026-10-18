#!/usr/bin/env python3
"""Memoria de conversación de Winy por WhatsApp (~30 días).

Guarda cada intercambio en historial.jsonl y lo va podando a 30 días. Se usa desde
process.sh:
  memoria.py render          -> imprime el historial reciente (para meterlo en el prompt)
  memoria.py add gerard      -> añade un mensaje de Gerard (texto por stdin)
  memoria.py add winy        -> añade una respuesta de Winy (texto por stdin)
"""
import json
import os
import sys
import time

RESP = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(RESP, "historial.jsonl")
DAYS = 30          # ventana de memoria (lo que se GUARDA en disco)
MAX_RENDER = 16    # mensajes que se INYECTAN al prompt = 8 intercambios (hilo suficiente)
MAX_CHARS = 280    # recorte por mensaje al inyectarlo (las respuestas de Winy son largas)


def prune_and_load():
    cutoff = time.time() - DAYS * 86400
    rows = []
    try:
        with open(HIST, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("ts", 0) >= cutoff:
                    rows.append(o)
    except FileNotFoundError:
        return []
    # reescribe el archivo ya podado
    tmp = HIST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for o in rows:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    os.replace(tmp, HIST)
    return rows


def render():
    """Historial reciente para el prompt: pocos mensajes y recortados.

    Se guardan 30 días, pero al prompt solo va el hilo cercano: inyectar el mes entero
    disparaba el contexto (y el coste) en cada mensaje.
    """
    rows = prune_and_load()[-MAX_RENDER:]
    out = []
    for o in rows:
        who = "Gerard" if o.get("role") == "gerard" else "Winy"
        text = (o.get("text") or "").strip()
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rstrip() + " […]"
        out.append(f"{who}: {text}")
    sys.stdout.write("\n".join(out))


def add(role):
    text = sys.stdin.read().strip()
    if not text:
        return
    with open(HIST, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": int(time.time()), "role": role, "text": text},
                           ensure_ascii=False) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "render":
        render()
    elif cmd == "add":
        add(sys.argv[2] if len(sys.argv) > 2 else "gerard")
    else:
        sys.exit(1)
