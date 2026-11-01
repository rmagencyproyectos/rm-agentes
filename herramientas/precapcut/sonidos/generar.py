#!/usr/bin/env python3
"""Genera la librería de efectos de precapcut (fase 3) por síntesis: sin descargas ni licencias.
Cortos, suaves y normalizados (pico -3 dBFS). Uso: python3 generar.py  →  *.wav + sonidos.json"""
import json
import wave
from pathlib import Path

import numpy as np

SR = 48000
AQUI = Path(__file__).resolve().parent
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, ataque=0.005, caida=0.1):
    x = np.arange(n) / SR
    return np.minimum(1, x / max(ataque, 1e-4)) * np.exp(-x / caida)


def filtro_paso_bajo(x, corte):
    a = np.exp(-2 * np.pi * corte / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # un polo: suficiente para efectos cortos
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def barrido_ruido(d, f0, f1, forma):
    n = rng.standard_normal(int(SR * d))
    cortes = np.geomspace(f0, f1, len(n))
    out, acc = np.empty_like(n), 0.0
    for i, (v, c) in enumerate(zip(n, cortes)):
        a = np.exp(-2 * np.pi * c / SR)
        acc = (1 - a) * v + a * acc
        out[i] = acc
    return out * forma(np.linspace(0, 1, len(n)))


SONIDOS = {
    "pop": ("pop", "entrada de un titular o elemento", lambda: np.sin(2 * np.pi * np.cumsum(np.geomspace(900, 380, int(SR * .09))) / SR) * env(int(SR * .09), .002, .03)),
    "pop_suave": ("pop", "entrada discreta", lambda: np.sin(2 * np.pi * np.cumsum(np.geomspace(600, 300, int(SR * .08))) / SR) * env(int(SR * .08), .004, .025)),
    "click": ("click", "botón, tocar algo, «guardar»", lambda: filtro_paso_bajo(rng.standard_normal(int(SR * .03)), 4000) * env(int(SR * .03), .0005, .006)),
    "whoosh": ("whoosh", "cambio de plano real", lambda: barrido_ruido(.45, 300, 4000, lambda u: np.sin(np.pi * u) ** 2)),
    "whoosh_corto": ("whoosh", "transición rápida", lambda: barrido_ruido(.25, 500, 6000, lambda u: np.sin(np.pi * u) ** 2)),
    "swoosh_bajada": ("swoosh", "algo que sale o baja", lambda: barrido_ruido(.35, 5000, 400, lambda u: np.sin(np.pi * u) ** 2)),
    "impacto": ("impact", "exclamación / golpe de efecto", lambda: (np.sin(2 * np.pi * np.cumsum(np.geomspace(120, 45, int(SR * .5))) / SR) * env(int(SR * .5), .002, .15)
                                                             + 0.4 * filtro_paso_bajo(rng.standard_normal(int(SR * .5)), 1500) * env(int(SR * .5), .001, .05))),
    "ding": ("ding", "acierto, dato bueno", lambda: sum(a * np.sin(2 * np.pi * f * t(.9)) for f, a in ((1320, 1), (2640, .3), (3960, .12))) * env(int(SR * .9), .002, .25)),
    "check": ("check", "visto bueno (dos notas que suben)", lambda: np.concatenate([np.sin(2 * np.pi * 880 * t(.09)) * env(int(SR * .09), .002, .05),
                                                                                    np.sin(2 * np.pi * 1320 * t(.35)) * env(int(SR * .35), .002, .12)])),
    "error": ("error", "lo que NO hay que hacer (dos notas que bajan)", lambda: np.concatenate([np.sin(2 * np.pi * 440 * t(.12)) * env(int(SR * .12), .002, .07),
                                                                                              np.sin(2 * np.pi * 330 * t(.3)) * env(int(SR * .3), .002, .1)])),
    "riser": ("riser", "antes de algo importante / CTA", lambda: barrido_ruido(1.2, 200, 6000, lambda u: u ** 2 * (1 - np.clip((u - .95) * 20, 0, 1)))),
    "obturador": ("camera", "foto, «mira esto»", lambda: np.concatenate([filtro_paso_bajo(rng.standard_normal(int(SR * .04)), 6000) * env(int(SR * .04), .0005, .01),
                                                                        np.zeros(int(SR * .05)),
                                                                        filtro_paso_bajo(rng.standard_normal(int(SR * .05)), 3000) * env(int(SR * .05), .0005, .015)])),
    "notificacion": ("notification", "aviso suave", lambda: np.concatenate([np.sin(2 * np.pi * 988 * t(.1)) * env(int(SR * .1), .003, .06),
                                                                           np.sin(2 * np.pi * 1480 * t(.3)) * env(int(SR * .3), .003, .1)])),
}


def guardar(nombre, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-3 / 20)  # pico a -3 dBFS
    x = np.concatenate([x, np.zeros(int(SR * .02))])
    with wave.open(str(AQUI / f"{nombre}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return len(x) / SR


if __name__ == "__main__":
    manifiesto = []
    for nombre, (cat, uso, fn) in SONIDOS.items():
        dur = guardar(nombre, fn())
        manifiesto.append({"id": nombre, "archivo": f"{nombre}.wav", "categoria": cat, "duracion": round(dur, 3),
                           "cuando": uso, "licencia": "propia (sintetizado por generar.py)", "fuente": "generar.py"})
    (AQUI / "sonidos.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(manifiesto)} sonidos")
