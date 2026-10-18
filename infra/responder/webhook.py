#!/usr/bin/env python3
"""Winy conversacional — receptor de WhatsApp entrante.

Evolution API (en Docker) llama a este servidor cuando llega un mensaje. Filtra para que
SOLO procese mensajes del propio número de Gerard, ignora los que manda la propia Winy
(por id ya enviado o por la marca invisible), descarta mensajes viejos, y lanza process.sh
que corre Winy y responde. Escucha en 0.0.0.0:<PORT> y exige un token secreto en la ruta.
"""
import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
RESP = os.path.join(HUB, "infra/responder")
SENT = os.path.join(RESP, "sent-ids.log")
SEEN = os.path.join(RESP, "seen-ids.log")

TOKEN = os.environ.get("WEBHOOK_TOKEN", "")
PORT = int(os.environ.get("WEBHOOK_PORT", "8790"))
OWNER = os.environ.get("WA_DESTINO", "")
MARK = "​"  # zero-width space que Winy pone en sus propios mensajes (anti-bucle)
MAX_AGE = 180    # segundos: ignora mensajes más viejos (evita reprocesar al arrancar)


def owner_num(jid):
    return (jid or "").split("@")[0].split(":")[0]


OWNER_NUM = owner_num(OWNER)


def load_ids(path):
    try:
        with open(path) as f:
            return set(l.strip() for l in f if l.strip())
    except FileNotFoundError:
        return set()


def mark(path, i):
    with open(path, "a") as f:
        f.write(i + "\n")


def extract_text(msg):
    if not isinstance(msg, dict):
        return ""
    return (msg.get("conversation")
            or (msg.get("extendedTextMessage") or {}).get("text")
            or "")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        # Token secreto en la ruta (…/hook/<TOKEN>)
        if TOKEN and self.path.rstrip("/").split("/")[-1] != TOKEN:
            self.send_response(403); self.end_headers(); return
        n = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(n) if n else b""
        # Responder rápido a Evolution y procesar aparte
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        try:
            body = json.loads(raw or b"{}")
        except Exception:
            return
        if body.get("event") != "messages.upsert":
            return
        data = body.get("data") or {}
        items = data if isinstance(data, list) else [data]
        for it in items:
            self.handle_msg(it)

    def handle_msg(self, it):
        if not isinstance(it, dict):
            return
        key = it.get("key") or {}
        jid = key.get("remoteJid", "")
        mid = key.get("id", "")
        # SOLO el número de Gerard
        if not mid or owner_num(jid) != OWNER_NUM:
            return
        # Descartar viejos
        ts = it.get("messageTimestamp") or 0
        try:
            ts = int(ts)
        except Exception:
            ts = 0
        if ts and (time.time() - ts) > MAX_AGE:
            return
        # Anti-bucle: ignorar lo que ya enviamos o ya vimos
        if mid in load_ids(SENT) or mid in load_ids(SEEN):
            return
        msg = it.get("message") or {}
        text = extract_text(msg)
        if text and text.strip():
            # Anti-bucle robusto: si trae la marca invisible, es un mensaje de la propia Winy
            if MARK in text:
                return
            mark(SEEN, mid)
            subprocess.Popen(["/bin/bash", os.path.join(RESP, "process.sh"), text])
            return
        # ¿es una nota de voz / audio? -> transcribir. Aceptamos varias formas conocidas.
        is_audio = False
        if isinstance(msg, dict):
            if "audioMessage" in msg or "pttMessage" in msg:
                is_audio = True
            mt = (it.get("messageType") or "").lower()
            if "audio" in mt or mt in ("ptt", "voice"):
                is_audio = True
        if is_audio:
            mark(SEEN, mid)
            subprocess.Popen(["/bin/bash", os.path.join(RESP, "process.sh"), "__AUDIO__", mid])
            return
        # Otro tipo (imagen, sticker, etc.) -> por ahora se ignora


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
