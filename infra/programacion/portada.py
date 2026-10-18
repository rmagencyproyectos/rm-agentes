#!/usr/bin/env python3
"""Ayuda a elegir la PORTADA de un vídeo antes de programarlo en Metricool.

Regla de Gerard (09/10/2026): la portada/miniatura de cada vídeo tiene que ser el momento en
que se ve el TEXTO PRINCIPAL (el título grande del gancho), no un fotograma cualquiera.

Metricool lo guarda como `videoCoverMilliseconds` (milisegundo del vídeo que hace de portada).
Este script NO decide: saca fotogramas para que quien programa (Claude en sesión) los mire y
elija el milisegundo. Luego ese valor va como `portada_ms` en el post de `metricool.json` y
`programar.py` lo manda.

Uso (con /usr/bin/python3, que es el que tiene las libs de Drive):
  portada.py --drive-id <id>                 -> hojas de 1 fotograma/seg (16 por hoja)
  portada.py --drive-id <id> --fino 2.4      -> 12 fotogramas cada 0,2 s desde ese segundo
  portada.py --drive-id <id> --frame 3.6     -> ese fotograma a 540 px, para confirmar
  (--video <ruta.mp4> en vez de --drive-id si ya está en local)
Imprime las rutas de las imágenes. El vídeo se cachea en --out para no bajarlo dos veces.

ffmpeg: no está instalado en el sistema; se usa el binario que trae `imageio_ffmpeg` en el
site-packages de usuario de Python 3.12.
"""
import argparse
import glob
import os
import subprocess
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/metricool"))


def ffmpeg():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/Library/Python/*/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-*")))
    if not cands:
        sys.exit("No encuentro ffmpeg (instala imageio-ffmpeg: python3.12 -m pip install --user imageio-ffmpeg).")
    return cands[-1]


def video_local(a):
    if a.video:
        return a.video
    destino = os.path.join(a.out, f"{a.drive_id}.mp4")
    if not os.path.exists(destino):
        import subir_media
        from programar import load_env
        data, _, _ = subir_media.descargar_de_drive(load_env(), a.drive_id)
        with open(destino, "wb") as f:
            f.write(data)
    return destino


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--drive-id")
    g.add_argument("--video")
    p.add_argument("--out", default="/tmp/rm-portadas")
    p.add_argument("--segundos", type=int, default=32, help="Cuántos segundos mirar (por defecto 32)")
    p.add_argument("--fino", type=float, help="Segundo desde el que sacar 12 fotogramas cada 0,2 s")
    p.add_argument("--frame", type=float, help="Segundo exacto a extraer en grande")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    v = video_local(a)
    ff = ffmpeg()
    base = os.path.join(a.out, os.path.splitext(os.path.basename(v))[0])

    if a.frame is not None:
        out = f"{base}_frame_{int(a.frame * 1000)}.png"
        subprocess.run([ff, "-v", "error", "-y", "-ss", str(a.frame), "-i", v, "-frames:v", "1",
                        "-vf", "scale=540:-1", out], check=True)
        print(out)
    elif a.fino is not None:
        out = f"{base}_fino_{int(a.fino * 1000)}.png"
        subprocess.run([ff, "-v", "error", "-y", "-ss", str(a.fino), "-t", "2.4", "-i", v,
                        "-vf", "fps=5,scale=200:-1,tile=6x2", "-frames:v", "1", out], check=True)
        print(out, "  (12 fotogramas: el n-ésimo es", a.fino, "+ 0,2·n s, de izquierda a derecha)")
    else:
        patron = f"{base}_hoja_%02d.png"
        subprocess.run([ff, "-v", "error", "-y", "-t", str(a.segundos), "-i", v,
                        "-vf", "fps=1,scale=200:-1,tile=8x2", patron], check=True)
        for h in sorted(glob.glob(f"{base}_hoja_*.png")):
            print(h)
        print("(cada hoja = 16 s, un fotograma por segundo, de izquierda a derecha y arriba abajo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
