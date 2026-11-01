#!/usr/bin/env python3
"""Librería de efectos de precapcut: efectos REALES de Mixkit (licencia gratuita para uso comercial, sin
atribución: https://mixkit.co/license/#sfxFree). Gerard 01/11: «usaremos los que ya están validados».
Descarga, quita solo el silencio del principio (nunca la cola), fade corto al final, pico a -1 dBFS.
Uso: python3 descargar.py   (lo lanzan los instaladores si faltan los .wav)"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from precapcut import ffmpeg_bin  # noqa: E402

BASE = "https://assets.mixkit.co/active_storage/sfx/{0}/{0}-preview.mp3"
EFECTOS = [  # id, mixkit, nombre en Mixkit, categoría, cuándo
    ("whoosh", 1489, "Air woosh", "whoosh", "cambio de plano real (ligero)"),
    ("whoosh_corto", 1490, "Fast whoosh transition", "whoosh", "entrada de exclamación / transición rápida"),
    ("pop_suave", 3005, "Explainer video pops whoosh light pop", "pop", "entrada de un titular (uno por idea)"),
    ("pop", 2358, "Long pop", "pop", "entrada de un recurso"),
    ("click", 1113, "Mouse click close", "click", "botón, «guardar»"),
    ("impacto", 788, "Big cinematic impact", "impact", "exclamación / golpe de efecto"),
    ("check", 2865, "Success software tone", "check", "visto bueno, lo bueno"),
    ("error", 948, "Wrong answer bass buzzer", "error", "lo que NO hay que hacer"),
    ("notificacion", 2354, "Message pop alert", "notification", "aviso suave"),
    ("obturador", 1133, "Camera shutter click", "camera", "foto, «mira esto»"),
]


def main():
    ff, out = ffmpeg_bin(), []
    for ident, num, nombre, cat, uso in EFECTOS:
        mp3, wav = AQUI / f"{ident}.mp3", AQUI / f"{ident}.wav"
        if not wav.exists():
            req = urllib.request.Request(BASE.format(num), headers={"User-Agent": "Mozilla/5.0"})
            mp3.write_bytes(urllib.request.urlopen(req, timeout=60).read())
            # silencio inicial fuera; la cola entera con un fade de 30 ms al final; pico a -1 dBFS
            subprocess.run([ff, "-v", "error", "-y", "-i", str(mp3), "-af",
                            "silenceremove=start_periods=1:start_threshold=-50dB,areverse,afade=t=in:d=0.03,areverse,"
                            "loudnorm=I=-14:TP=-1:LRA=11:linear=true", "-ar", "48000", "-ac", "2", str(wav)], check=True)
            mp3.unlink()
        r = subprocess.run([ff, "-i", str(wav), "-f", "null", "-"], capture_output=True, text=True).stderr
        t = r.split("time=")[-1].split()[0].split(":")
        out.append({"id": ident, "archivo": wav.name, "categoria": cat, "duracion": round(float(t[0]) * 3600 + float(t[1]) * 60 + float(t[2]), 3),
                    "cuando": uso, "licencia": "Mixkit Sound Effects Free License (uso comercial, sin atribución)",
                    "fuente": f"https://mixkit.co · «{nombre}» · {BASE.format(num)}"})
    (AQUI / "sonidos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} efectos")


if __name__ == "__main__":
    main()
