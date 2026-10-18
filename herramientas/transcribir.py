#!/usr/bin/env python
"""Transcribe notas de voz en local con MLX Whisper (nada sale del Mac).

El audio se carga con el módulo wave en vez de con ffmpeg, que no está
instalado; conviértelo antes con opus2wav.swift.

    swift opus2wav.swift nota.opus nota.wav
    ~/.venvs/whisper/bin/python transcribir.py [--idioma ca] nota.wav

Ojo con el idioma: las notas de Magda son en catalán con castellano mezclado.
Si se le pasa el idioma equivocado, Whisper entra en bucle y repite frases.
"""
import sys
import wave

import numpy as np
import mlx_whisper

MODELO = "mlx-community/whisper-large-v3-turbo"


def leer_wav(ruta):
    with wave.open(ruta, "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1, "se espera WAV mono 16 bits"
        crudo = w.readframes(w.getnframes())
    return np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768.0


args = sys.argv[1:]
idioma = "es"
if "--idioma" in args:
    i = args.index("--idioma")
    idioma = args[i + 1]
    del args[i:i + 2]

for ruta in args:
    res = mlx_whisper.transcribe(leer_wav(ruta), path_or_hf_repo=MODELO,
                                 language=idioma, fp16=True)
    print("=" * 70)
    print(ruta)
    print("=" * 70)
    print(res["text"].strip())
    print()
