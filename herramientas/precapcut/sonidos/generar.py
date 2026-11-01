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


def boom():
    """Impacto de cine: golpe grave que baja de tono, cuerpo y cola larga (v1 sonaba cortado, Gerard 01/11)."""
    d = 1.6
    f = np.concatenate([np.geomspace(90, 42, int(SR * .18)), np.full(int(SR * (d - .18)), 42.0)])
    grave = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(f), .003, .55)
    golpe = filtro_paso_bajo(rng.standard_normal(len(f)), 2500) * env(len(f), .0005, .04) * 1.5
    cola = filtro_paso_bajo(rng.standard_normal(len(f)), 900) * env(len(f), .05, .5) * .25
    return np.tanh(1.8 * (grave + golpe + cola))  # algo de saturación: suena lleno y se oye con la voz


def click_raton():
    """Clic reconocible: pulsar y soltar (dos golpecitos con cuerpo de plástico)."""
    def tic(f0, amp):
        n = int(SR * .025)
        return amp * (np.sin(2 * np.pi * f0 * t(.025)) * env(n, .0003, .004)
                      + .5 * filtro_paso_bajo(rng.standard_normal(n), 7000) * env(n, .0002, .002))
    return np.concatenate([tic(3200, 1.0), np.zeros(int(SR * .045)), tic(2600, .6), np.zeros(int(SR * .05))])


def campana(notas, dur):
    return np.concatenate([sum(a * np.sin(2 * np.pi * f * k * t(d)) for k, a in ((1, 1), (2, .35), (3, .15))) * env(int(SR * d), .002, d / 3)
                           for f, d in zip(notas, dur)])


SONIDOS = {
    "pop": ("pop", "entrada de un titular o elemento", lambda: np.sin(2 * np.pi * np.cumsum(np.geomspace(900, 380, int(SR * .09))) / SR) * env(int(SR * .09), .002, .03)),
    "pop_suave": ("pop", "entrada discreta", lambda: np.sin(2 * np.pi * np.cumsum(np.geomspace(600, 300, int(SR * .08))) / SR) * env(int(SR * .08), .004, .025)),
    "click": ("click", "botón, tocar algo, «guardar» (clic de ratón)", click_raton),
    "whoosh": ("whoosh", "cambio de plano real (ligero: el grave pesaba, Gerard 01/11)", lambda: barrido_ruido(.32, 2000, 9000, lambda u: np.sin(np.pi * u) ** 3)),
    "whoosh_corto": ("whoosh", "transición rápida", lambda: barrido_ruido(.22, 3000, 10000, lambda u: np.sin(np.pi * u) ** 3)),
    "swoosh_bajada": ("swoosh", "algo que sale o baja", lambda: barrido_ruido(.35, 5000, 400, lambda u: np.sin(np.pi * u) ** 2)),
    "impacto": ("impact", "exclamación / golpe de efecto (boom con cola)", boom),
    "ding": ("ding", "acierto, dato bueno", lambda: sum(a * np.sin(2 * np.pi * f * t(.9)) for f, a in ((1320, 1), (2640, .3), (3960, .12))) * env(int(SR * .9), .002, .25)),
    "check": ("check", "visto bueno (dos notas que suben)", lambda: campana((880, 1318.5), (.12, .5))),
    "error": ("error", "lo que NO hay que hacer (dos notas graves que bajan)", lambda: np.tanh(2 * campana((311, 233), (.14, .45)))),
    "riser": ("riser", "antes de algo importante / CTA", lambda: barrido_ruido(1.2, 200, 6000, lambda u: u ** 2 * (1 - np.clip((u - .95) * 20, 0, 1)))),
    "obturador": ("camera", "foto, «mira esto»", lambda: np.concatenate([filtro_paso_bajo(rng.standard_normal(int(SR * .04)), 6000) * env(int(SR * .04), .0005, .01),
                                                                        np.zeros(int(SR * .05)),
                                                                        filtro_paso_bajo(rng.standard_normal(int(SR * .05)), 3000) * env(int(SR * .05), .0005, .015)])),
    "notificacion": ("notification", "aviso suave", lambda: np.concatenate([np.sin(2 * np.pi * 988 * t(.1)) * env(int(SR * .1), .003, .06),
                                                                           np.sin(2 * np.pi * 1480 * t(.3)) * env(int(SR * .3), .003, .1)])),
}


def guardar(nombre, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-1 / 20)  # pico a -1 dBFS: se tienen que oír
    fade = min(len(x) // 4, int(SR * .03))  # nunca cortado: la cola acaba en silencio
    x[-fade:] *= np.linspace(1, 0, fade)
    x = np.concatenate([x, np.zeros(int(SR * .03))])
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
