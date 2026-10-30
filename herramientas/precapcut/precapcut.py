#!/usr/bin/env python3
"""precapcut — deja vídeos medio editados en CapCut, por fases.

Fase 1 (esto): transcribe en local con tiempos por palabra, quita tomas falladas,
arranques en falso, muletillas y silencios, y monta el resultado en CapCut.

    precapcut.py fase1  <pieza> <video> [<video> ...] [--idioma ca|es] [--modelo medium]
    precapcut.py montar <pieza> [--en "<proyecto CapCut vacío>" | --nuevo "<nombre>"] [--sin-capcut]
    precapcut.py qa     <pieza>

Todo lo de una pieza vive en <trabajo>/<pieza>/ (por defecto ~/rmagency/work/precapcut/).
El modelo (Claude) solo lee `fase1.md`; nunca el vídeo ni los .json grandes.
Funciona en Mac y Windows: Python 3.9+, faster-whisper, capcut-cli (npm) y ffmpeg
(si no hay ffmpeg en el PATH usa el de imageio-ffmpeg).
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TRABAJO = Path(os.environ.get("PRECAPCUT_TRABAJO", Path.home() / "rmagency" / "work" / "precapcut"))

# Ajustes de corte (segundos). Probados contra el QA de Aprenent fotografia R01:
# márgenes 80 ms delante / 150 ms detrás no se comen sílabas.
PAD_ANTES = 0.08
PAD_DESPUES = 0.15
BUSCA_ANTES = 0.6     # Whisper da el inicio de palabra tarde (visto: "Poner" 0,34 s tarde): el corte se
BUSCA_DESPUES = 0.4   # lleva hasta donde empieza/acaba el sonido, mirando como mucho esto
PAUSA_MAX = 0.35      # pausa más larga que esto dentro de lo que se queda -> se recorta
GAP_FRASE = 0.55      # pausa que separa dos frases
VENTANA_TOMAS = 5     # cuántas frases hacia delante se busca la repetición
SIM_TOMA = 0.6        # parecido mínimo para considerar que es la misma frase repetida
SIM_ARRANQUE = 0.75   # parecido mínimo de un arranque en falso con el inicio de la frase buena
SIM_CONTENIDA = 0.75  # parte de una frase que se vuelve a decir dentro de otra posterior -> trozo de toma
PALABRA_MAX = 1.5     # una "palabra" más larga es audio que Whisper se ha tragado: se re-transcribe
SIM_INICIO = 0.8      # dos frases que arrancan igual (4+ palabras) son la misma toma empezada de nuevo


# ---------------------------------------------------------------- utilidades

def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("Falta ffmpeg: instala imageio-ffmpeg (pip) o ffmpeg.")


def entorno_capcut():
    """PATH con ffprobe para capcut-cli. Sin ffprobe, compile no sabe cuánto dura cada vídeo y
    da el material por acabado donde acaba el corte: en CapCut no se puede alargar ningún clip.
    Si no hay ffprobe se usa ffprobe_pyav.py (PyAV sí lee los MP4 de la Sony; el ffprobe de
    static-ffmpeg no: "infe version < 2")."""
    env = dict(os.environ)
    if shutil.which("ffprobe"):
        return env
    if sys.platform == "win32":  # Node solo encuentra .exe: el envoltorio no sirve en Windows
        sys.exit("Falta ffprobe (capcut-cli lo necesita para la duración real de los vídeos): "
                 "winget install Gyan.FFmpeg y vuelve a abrir la terminal.")
    bin_dir = TRABAJO / ".bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    envoltorio = bin_dir / "ffprobe"
    envoltorio.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{AQUI / "ffprobe_pyav.py"}" "$@"\n',
                          encoding="utf-8")
    envoltorio.chmod(0o755)
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    return env


def capcut_bin():
    exe = shutil.which("capcut") or shutil.which("capcut.cmd")
    if not exe:
        sys.exit("Falta capcut-cli: npm i -g capcut-cli")
    return exe


def sondear(video):
    """Duración, tamaño y fps con PyAV (viene con faster-whisper): no hace falta ffprobe."""
    import av
    with av.open(str(video)) as c:
        v = next((s for s in c.streams if s.type == "video"), None)
        dur = float(c.duration) / 1e6 if c.duration else None
        info = {"duracion": dur}
        if v is not None:
            w, h = v.codec_context.width, v.codec_context.height
            rot = 0
            try:
                rot = int(v.metadata.get("rotate", 0))
            except (TypeError, ValueError):
                pass
            if not rot:
                # FFmpeg 5+ ya no pone la etiqueta rotate: va en el displaymatrix,
                # que PyAV solo enseña en el primer fotograma decodificado.
                try:
                    rot = int(next(c.decode(v)).rotation or 0)
                except (StopIteration, AttributeError, av.error.FFmpegError):
                    pass
            if abs(rot) % 180 == 90:
                w, h = h, w
            info.update(ancho=w, alto=h, fps=float(v.average_rate or 30))
        return info


def norm(palabra):
    p = unicodedata.normalize("NFKD", palabra.lower())
    p = "".join(ch for ch in p if not unicodedata.combining(ch))
    return re.sub(r"[^\w']", "", p).strip("'")


def tc(seg):
    m, s = divmod(max(seg, 0), 60)
    return f"{int(m)}:{s:05.2f}"


def cargar_vocabulario():
    """vocabulario.txt: palabras que el modelo debe escribir bien + correcciones `mal => bien`."""
    pistas, fixes = [], {}
    f = AQUI / "vocabulario.txt"
    if f.exists():
        for linea in f.read_text(encoding="utf-8").splitlines():
            linea = linea.split("#", 1)[0].strip()
            if not linea:
                continue
            if "=>" in linea:
                mal, bien = (x.strip() for x in linea.split("=>", 1))
                fixes[mal.lower()] = bien
            else:
                pistas.append(linea)
    return pistas, fixes


def leer_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def escribir_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- transcripción

_MODELOS = {}


def transcribir(video, idioma, modelo, cache_dir):
    """Palabras con tiempos. Cachea por nombre+tamaño+fecha: re-ejecutar no repite el trabajo."""
    st = Path(video).stat()
    clave = f"{Path(video).stem}-{st.st_size}-{int(st.st_mtime)}-{modelo}-{idioma or 'auto'}-v2"
    cache = cache_dir / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', clave)}.json"
    if cache.exists():
        return leer_json(cache)

    from faster_whisper import WhisperModel
    pistas, fixes = cargar_vocabulario()
    print(f"  transcribiendo {Path(video).name} (modelo {modelo})...", flush=True)
    if modelo not in _MODELOS:  # cargarlo una vez por ejecución, no una por vídeo
        _MODELOS[modelo] = WhisperModel(modelo, device="auto", compute_type="int8")
    m = _MODELOS[modelo]
    def pasada(audio, idioma, desfase=0.0):
        segs, info = m.transcribe(
            audio,
            language=idioma,
            word_timestamps=True,
            # Sin VAD y sin arrastrar contexto: así Whisper NO "limpia" las repeticiones,
            # que es justo lo que queremos ver para quitar las tomas falladas.
            vad_filter=False,
            condition_on_previous_text=False,
            initial_prompt=", ".join(pistas) if pistas else None,
        )
        palabras = []
        for s in segs:
            for w in s.words or []:
                txt = w.word.strip()
                if not txt:
                    continue
                txt = fixes.get(txt.lower().strip(".,;:!?"), txt) if fixes else txt
                palabras.append({"w": txt, "s": round(w.start + desfase, 3),
                                 "e": round(w.end + desfase, 3), "p": round(w.probability, 2)})
        return palabras, info.language

    palabras, idioma_real = pasada(str(video), idioma)
    # Sin VAD, Whisper a veces se salta una toma entera y estira una palabra por encima
    # (visto: "cuberteros" de 9,5 s que escondía la toma fallada y una charla). Ese tramo
    # se vuelve a transcribir solo y sus palabras sustituyen a la estirada.
    largas = [w for w in palabras if w["e"] - w["s"] > PALABRA_MAX]
    if largas:
        from faster_whisper import decode_audio
        audio, sr = decode_audio(str(video)), 16000
        for w in largas:
            trozo = audio[int(w["s"] * sr):int(w["e"] * sr)]
            nuevas, _ = pasada(trozo, idioma_real, w["s"])
            if nuevas:
                k = palabras.index(w)
                palabras[k:k + 1] = nuevas
        print(f"    {len(largas)} palabra(s) estirada(s) re-transcrita(s)", flush=True)
    data = {"video": str(Path(video).resolve()), "idioma": idioma_real, "palabras": palabras}
    escribir_json(cache, data)
    return data


# ---------------------------------------------------------------- análisis fase 1

# "este" NO: en castellano casi siempre es "este vídeo", no una muletilla.
MULETILLAS = {"eh", "ehm", "em", "emm", "mm", "mmm", "hmm", "uh", "um", "eeh", "eee"}


def partir_frases(palabras):
    frases, actual = [], []
    for w in palabras:
        if actual:
            gap = w["s"] - actual[-1]["e"]
            fin = actual[-1]["w"].endswith((".", "?", "!"))
            if gap >= GAP_FRASE or (fin and gap >= 0.2):
                frases.append(actual)
                actual = []
        actual.append(w)
    if actual:
        frases.append(actual)
    return frases


def similitud(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def contenida(a, b):
    """Qué parte de `a` se vuelve a decir, en orden, dentro de `b` (solo tramos de 2+ palabras:
    "que", "de", "la" sueltos coinciden con cualquier cosa)."""
    if not a or not b:
        return 0.0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(m.size for m in sm.get_matching_blocks() if m.size >= 2) / len(a)


def repeticiones_internas(ws):
    """'i dos, i dos perquè...' -> marca la primera copia. Devuelve índices a quitar."""
    toks = [norm(w["w"]) for w in ws]
    quitar = set()
    for n in range(5, 0, -1):
        i = 0
        while i + 2 * n <= len(toks):
            a, b = toks[i:i + n], toks[i + n:i + 2 * n]
            # la última palabra de la copia puede estar cortada: "m'ani" / "m'aniria"
            igual = a[:-1] == b[:-1] and a[-1] and b[-1].startswith(a[-1])
            if igual and not (n == 1 and len(a[0]) <= 2) and not any(j in quitar for j in range(i, i + n)):
                quitar.update(range(i, i + n))
                i += n
            else:
                i += 1
    return quitar


def analizar(transcripciones):
    """Decide qué se queda. Devuelve la lista de frases con su decisión y motivo."""
    frases = []
    for vi, t in enumerate(transcripciones):
        for ws in partir_frases(t["palabras"]):
            frases.append({"video": vi, "palabras": ws})

    for i, f in enumerate(frases):
        f["id"] = f"F{i + 1:03d}"
        f["queda"] = True
        f["motivo"] = ""
        f["quitar_palabras"] = []

    # 1) tomas repetidas y arranques en falso: gana la ÚLTIMA toma (la buena suele ser la última)
    toks = [[norm(w["w"]) for w in f["palabras"]] for f in frases]
    for i, f in enumerate(frases):
        a = [x for x in toks[i] if x and x not in MULETILLAS]
        if not a:
            continue
        # la repetición puede estar en el clip siguiente: se suele parar y volver a grabar
        for j in range(i + 1, min(i + 1 + VENTANA_TOMAS, len(frases))):
            b = [x for x in toks[j] if x and x not in MULETILLAS]
            if not b:
                continue
            completa = similitud(a, b)
            arranque = similitud(a, b[:len(a)]) if len(a) < len(b) else 0
            k = min(len(a), len(b))
            inicio = similitud(a[:k], b[:k]) if k >= 4 else 0
            if len(os.path.commonprefix([a, b])) >= 4:  # mismas 4 primeras palabras: misma toma
                inicio = 1.0
            # una toma partida en varias frases ("...así que guárdate este vídeo" / "para no
            # perderlas") no se parece entera a la buena, pero está dentro de ella
            # y una toma que se tuerce a media frase ("...guarda este mensaje, así que guarda
            # este vídeo") se reconoce porque la siguiente empieza con las mismas palabras
            if len(a) >= 3 and (completa >= SIM_TOMA or contenida(a, b) >= SIM_CONTENIDA
                                or inicio >= SIM_INICIO):
                f["queda"], f["motivo"] = False, f"toma repetida (se queda {frases[j]['id']})"
                break
            # una sola palabra corta ("no", "y", "que") no es un arranque en falso
            larga = len(a) >= 2 or len(a[0]) >= 4
            if larga and arranque >= SIM_ARRANQUE and len(b) - len(a) >= 2:
                f["queda"], f["motivo"] = False, f"arranque en falso (sigue en {frases[j]['id']})"
                break

    # 2) dentro de las frases que se quedan: repeticiones pegadas y muletillas
    for f, t in zip(frases, toks):
        if not f["queda"]:
            continue
        quitar = repeticiones_internas(f["palabras"])
        quitar |= {k for k, x in enumerate(t) if x in MULETILLAS}
        if len(quitar) >= len(f["palabras"]):
            f["queda"], f["motivo"] = False, "solo muletillas"
        elif quitar:
            f["quitar_palabras"] = sorted(quitar)
            f["motivo"] = "se limpian: " + " ".join(f["palabras"][k]["w"] for k in sorted(quitar))
    return frases


def envolvente(video):
    """Energía del audio en dB cada 10 ms y el umbral de silencio del clip: suelo de ruido + 20 dB,
    pero nunca más de 35 dB por debajo de la voz (con un suelo muy bajo, la reverberación
    contaba como sonido y no se encontraba el silencio antes de "así que")."""
    import numpy as np
    from faster_whisper import decode_audio
    a = decode_audio(str(video))
    n = len(a) // 160
    db = 20 * np.log10(np.sqrt((a[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9)
    suelo, voz = np.percentile(db, [10, 90])
    return db, min(max(float(suelo) + 20, float(voz) - 35), -25.0)


def nivel(env, t):
    db = env[0]
    k = min(max(int(t * 100), 0), len(db) - 1)
    return float(db[k:k + 3].mean())


def valle(env, a, b):
    """El punto más silencioso (media de 30 ms) entre a y b."""
    ks = range(int(a * 100), max(int(b * 100) - 2, int(a * 100) + 1))
    return min(ks, key=lambda k: env[0][k:k + 3].mean()) / 100


def borde_sonido(env, t, paso, limite, quieto=0.1):
    """Desde `t` avanza (paso -1 hacia atrás, +1 hacia delante) mientras haya sonido y devuelve
    dónde empieza el silencio (`quieto` s seguidos). None si no lo encuentra antes de `limite`."""
    db, umbral = env
    k, quietos, n = int(t * 100), 0, max(int(quieto * 100), 1)
    for _ in range(int(limite * 100)):
        k += paso
        if not 0 <= k < len(db):
            return None
        quietos = quietos + 1 if db[k] < umbral else 0
        if quietos >= n:
            return (k - paso * (n - 1)) / 100
    return None


def primer_sonido(env, t, paso, limite):
    """Si `t` cae en silencio, dónde está el sonido más cercano en esa dirección (o None)."""
    db, umbral = env
    k = int(t * 100)
    if not 0 <= k < len(db) or db[k] >= umbral:
        return None
    for _ in range(int(limite * 100)):
        k += paso
        if not 0 <= k < len(db):
            return None
        if db[k] >= umbral:
            return k / 100
    return None


def segmentos(frases, transcripciones, envolventes=None):
    """Frases + decisiones -> tramos de vídeo a conservar, sin silencios."""
    tramos = []
    for vi, t in enumerate(transcripciones):
        todas = t["palabras"]
        quedan = []
        for f in frases:
            if f["video"] != vi or not f["queda"]:
                continue
            fuera = set(f["quitar_palabras"])
            quedan += [w for k, w in enumerate(f["palabras"]) if k not in fuera]
        if not quedan:
            continue
        # vecinas reales (incluidas las cortadas) para que el margen no se coma otra palabra
        orden = {id(w): k for k, w in enumerate(todas)}
        grupo = [quedan[0]]
        grupos = []
        for w in quedan[1:]:
            pegada = orden[id(w)] == orden[id(grupo[-1])] + 1
            if pegada and w["s"] - grupo[-1]["e"] <= PAUSA_MAX:
                grupo.append(w)
            else:
                grupos.append(grupo)
                grupo = [w]
        grupos.append(grupo)
        dur = t.get("duracion") or (todas[-1]["e"] + 1)
        for g in grupos:
            k0, k1 = orden[id(g[0])], orden[id(g[-1])]
            prev_e = todas[k0 - 1]["e"] if k0 > 0 else 0.0
            next_s = todas[k1 + 1]["s"] if k1 + 1 < len(todas) else dur
            ini, fin = g[0]["s"] - PAD_ANTES, g[-1]["e"] + PAD_DESPUES
            if envolventes:
                # delante basta un hueco de 60 ms: entre la respiración y la primera palabra no hay
                # más ("Seguro" en C0041), y con 100 ms el corte se llevaba también la respiración
                antes = borde_sonido(envolventes[vi], g[0]["s"], -1, BUSCA_ANTES, quieto=0.06)
                despues = borde_sonido(envolventes[vi], g[-1]["e"], +1, BUSCA_DESPUES)
                if antes is not None:  # el arranque de una "s" o una "f" queda por debajo del umbral
                    ini = min(ini, antes - PAD_ANTES)
                if despues is not None:
                    fin = max(fin, despues + 0.03)
                # y al revés: si Whisper alarga la palabra por el silencio, el corte se acerca
                empieza = primer_sonido(envolventes[vi], g[0]["s"], +1, 0.3)
                acaba = primer_sonido(envolventes[vi], g[-1]["e"], -1, 0.4)
                if empieza is not None:
                    ini = max(ini, empieza - PAD_ANTES)
                if acaba is not None:
                    fin = min(fin, acaba + PAD_DESPUES)
            ini = max(ini, prev_e + 0.02, 0.0)
            fin = min(fin, next_s - 0.02, dur)
            # última red: un corte nunca entra ni sale con sonido. Si lo hace (Whisper ha dado mal
            # el tiempo de la palabra vecina), se lleva al silencio más hondo hasta esa palabra.
            if envolventes:
                env = envolventes[vi]
                lim = max(prev_e + 0.02, ini - BUSCA_ANTES, 0.0)
                if nivel(env, ini) >= env[1] and ini - lim > 0.03:
                    ini = max(valle(env, lim, ini) - PAD_ANTES, lim)
                lim = min(next_s - 0.02, fin + BUSCA_DESPUES, dur)
                if nivel(env, fin) >= env[1] and lim - fin > 0.03:
                    fin = valle(env, fin, lim)
            if fin - ini > 0.15:
                tramos.append({"video": vi, "ini": round(ini, 3), "fin": round(fin, 3),
                               "palabras": [dict(w) for w in g]})
    # posición en la línea de tiempo + palabras ya colocadas (las usa la fase 2)
    t = 0.0
    for tr in tramos:
        tr["tl"] = round(t, 3)
        for w in tr["palabras"]:
            w["ts"] = round(w["s"] - tr["ini"] + t, 3)
            w["te"] = round(w["e"] - tr["ini"] + t, 3)
        t += tr["fin"] - tr["ini"]
    return tramos


def informe(pieza, frases, transcripciones, tramos):
    total = sum(t.get("duracion") or 0 for t in transcripciones)
    final = sum(tr["fin"] - tr["ini"] for tr in tramos)
    fuera = [f for f in frases if not f["queda"]]
    out = [f"# Fase 1 · {pieza}", "",
           f"Bruto {tc(total)} → montado {tc(final)} · {len(tramos)} cortes · "
           f"{len(fuera)} frases fuera de {len(frases)}.", "",
           "Para cambiar una decisión edita `decisiones.json` (queda true/false) y vuelve a montar.", "",
           "| Frase | Vídeo | Tiempo | Queda | Texto | Motivo |", "|---|---|---|---|---|---|"]
    for f in frases:
        txt = " ".join(w["w"] for w in f["palabras"]).replace("|", "/")
        dudosas = [w["w"] for w in f["palabras"] if w["p"] < 0.5]
        motivo = f["motivo"] + (f" · dudoso: {', '.join(dudosas)}" if dudosas else "")
        out.append(f"| {f['id']} | {f['video'] + 1} | {tc(f['palabras'][0]['s'])} | "
                   f"{'✓' if f['queda'] else '✗'} | {txt} | {motivo} |")
    out += ["", "Vídeos:"] + [f"{i + 1}. {Path(t['video']).name}" for i, t in enumerate(transcripciones)]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- comandos

def cmd_fase1(a):
    d = TRABAJO / a.pieza
    (d / "cache").mkdir(parents=True, exist_ok=True)
    trans = []
    for v in a.videos:
        t = transcribir(v, a.idioma, a.modelo, d / "cache")
        t.update(sondear(v))
        trans.append(t)
    frases = analizar(trans)
    escribir_json(d / "transcripciones.json", trans)
    # volver a lanzar fase1 no borra lo decidido a mano (marcado "a_mano": true) si la frase es la misma
    previas = {}
    if (d / "decisiones.json").exists():
        previas = {(x["id"], x["texto"]): x for x in leer_json(d / "decisiones.json") if x.get("a_mano")}
    decis = []
    for f in frases:
        x = {"id": f["id"], "queda": f["queda"], "motivo": f["motivo"],
             "quitar_palabras": f["quitar_palabras"], "texto": " ".join(w["w"] for w in f["palabras"])}
        x = previas.get((x["id"], x["texto"]), x)
        f["queda"], f["motivo"], f["quitar_palabras"] = x["queda"], x["motivo"], x["quitar_palabras"]
        decis.append(x)
    escribir_json(d / "decisiones.json", decis)
    tramos = segmentos(frases, trans, [envolvente(t["video"]) for t in trans])
    (d / "fase1.md").write_text(informe(a.pieza, frases, trans, tramos), encoding="utf-8")
    print(f"Listo: {d / 'fase1.md'}")


def cargar_pieza(pieza):
    d = TRABAJO / pieza
    trans = leer_json(d / "transcripciones.json")
    frases = analizar(trans)
    decis = {x["id"]: x for x in leer_json(d / "decisiones.json")}
    for f in frases:  # lo que se haya cambiado a mano en decisiones.json manda
        x = decis.get(f["id"])
        if x:
            f["queda"] = bool(x["queda"])
            f["quitar_palabras"] = x.get("quitar_palabras", f["quitar_palabras"])
            f["motivo"] = x.get("motivo", f["motivo"])
    return d, trans, frases, segmentos(frases, trans, [envolvente(t["video"]) for t in trans])


def render_preview(trans, tramos, salida, alto=960):
    ff = ffmpeg_bin()
    entradas, filtros = [], []
    for i, t in enumerate(trans):
        entradas += ["-i", t["video"]]
    for k, tr in enumerate(tramos):
        v = tr["video"]
        filtros.append(f"[{v}:v]trim={tr['ini']}:{tr['fin']},setpts=PTS-STARTPTS,"
                       f"scale=-2:{alto},fps=30[v{k}]")
        filtros.append(f"[{v}:a]atrim={tr['ini']}:{tr['fin']},asetpts=PTS-STARTPTS[a{k}]")
    pares = "".join(f"[v{k}][a{k}]" for k in range(len(tramos)))
    filtros.append(f"{pares}concat=n={len(tramos)}:v=1:a=1[v][a]")
    script = Path(salida).with_suffix(".filtros.txt")
    script.write_text(";\n".join(filtros), encoding="utf-8")
    cmd = [ff, "-y", "-v", "error", *entradas, "-filter_complex_script", str(script),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
           "-c:a", "aac", "-b:a", "128k", str(salida)]
    subprocess.run(cmd, check=True)


def spec_capcut(nombre, trans, tramos):
    info = trans[0]
    ancho, alto = info.get("ancho") or 1080, info.get("alto") or 1920
    escala = 1920 / max(ancho, alto)
    w, h = round(ancho * escala / 2) * 2, round(alto * escala / 2) * 2
    items = [{"path": trans[tr["video"]]["video"], "start": tr["tl"],
              "sourceStart": tr["ini"], "duration": round(tr["fin"] - tr["ini"], 3)}
             for tr in tramos]
    return {"name": nombre, "width": w, "height": h, "fps": 30,
            "tracks": [{"type": "video", "name": "Cortes", "items": items}]}


def carpeta_borradores():
    if sys.platform == "darwin":
        return Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"
    return Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut/User Data/Projects/com.lveditor.draft"


def capcut_abierto():
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
            return "CapCut.exe" in out
        return subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def vaciar_proyecto(destino):
    """Quita los cortes de un montaje anterior de precapcut para volver a montar encima."""
    r = subprocess.run([capcut_bin(), "segments", str(destino)], capture_output=True, text=True, check=True)
    for seg in json.loads(r.stdout or "[]"):
        subprocess.run([capcut_bin(), "remove", str(destino), seg["id"], "-q"], check=True)


def cmd_montar(a):
    d, trans, frases, tramos = cargar_pieza(a.pieza)
    escribir_json(d / "timeline.json", {"tramos": tramos, "videos": [t["video"] for t in trans]})
    with open(d / "edl.csv", "w", encoding="utf-8") as f:
        f.write("n,video,entrada,salida,linea_tiempo,texto\n")
        for k, tr in enumerate(tramos, 1):
            txt = " ".join(w["w"] for w in tr["palabras"]).replace('"', "'")
            f.write(f'{k},"{Path(trans[tr["video"]]["video"]).name}",{tr["ini"]},{tr["fin"]},{tr["tl"]},"{txt}"\n')
    print(f"{len(tramos)} tramos, {tc(sum(t['fin'] - t['ini'] for t in tramos))} en total")
    # fase1.md con las decisiones finales (las de decisiones.json, también las tocadas a mano)
    (d / "fase1.md").write_text(informe(a.pieza, frases, trans, tramos), encoding="utf-8")

    render_preview(trans, tramos, d / "preview.mp4")
    print(f"Preview: {d / 'preview.mp4'}")
    if a.sin_capcut:
        return

    if capcut_abierto():
        sys.exit("CapCut está abierto: ciérralo y vuelve a lanzar `montar` (no se ha escrito nada).")
    spec = spec_capcut(a.nuevo or a.pieza, trans, tramos)
    escribir_json(d / "spec-fase1.json", spec)
    cmd = [capcut_bin(), "compile", str(d / "spec-fase1.json")]
    marca = d / "capcut-proyecto.txt"  # el proyecto que ya ha llenado precapcut para esta pieza
    nuestro = marca.read_text(encoding="utf-8").strip() if marca.exists() else None
    if a.en:
        destino = Path(a.en)
        if not destino.exists():
            destino = carpeta_borradores() / a.en
        if not destino.exists():
            sys.exit(f"No encuentro el proyecto de CapCut «{a.en}».")
    else:
        destino = carpeta_borradores() / spec["name"]
        if destino.exists() and str(destino) != nuestro:
            sys.exit(f"Ya hay un proyecto de CapCut «{spec['name']}» que no es de precapcut: usa otro --nuevo.")
    if destino.exists():
        copia = d / "backups" / destino.name
        if copia.exists():  # la primera copia (el proyecto tal cual estaba) no se pisa nunca
            copia = copia.with_name(f"{destino.name}-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copytree(destino, copia)
        if str(destino) == nuestro:
            vaciar_proyecto(destino)  # `compile --into` solo acepta proyectos vacíos
        cmd += ["--into", str(destino)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=entorno_capcut())
    print(r.stdout[-1500:] or r.stderr[-1500:])
    if r.returncode != 0:
        sys.exit("capcut compile ha fallado (ver arriba).")
    marca.write_text(str(destino), encoding="utf-8")
    try:
        destino = Path(json.loads(r.stdout.splitlines()[0]).get("draft_path", destino))
    except (ValueError, IndexError):
        pass
    apuntar_originales(destino,
                       {Path(t["video"]).name: t["video"] for t in trans})


def apuntar_originales(destino, originales):
    """Cada vídeo del proyecto apunta al original de la carpeta con su duración entera, en TODAS
    las copias que lee CapCut: draft_info/draft_content/template-2.tmp (raíz y Timelines/<id>/) y
    la lista del panel de medios de draft_meta_info.json. Esa lista no la toca capcut-cli y es la
    que manda: con la duración del corte, CapCut no deja alargar el clip."""
    largos = {}
    for nombre, ruta in originales.items():
        dur = sondear(ruta)["duracion"]
        largos[nombre] = (ruta, int(round(dur * 1e6)) if dur else None)
    cambios = 0
    mirrors = [f for patron in ("draft_info.json", "draft_content.json", "template-2.tmp")
               for f in [destino / patron, *destino.glob(f"Timelines/*/{patron}")] if f.exists()]
    for f in mirrors:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for m in data.get("materials", {}).get("videos", []):
            x = largos.get(Path(m.get("path", "")).name)
            if x:
                m["path"] = x[0]
                m["duration"] = max(m.get("duration") or 0, x[1] or 0)
                cambios += 1
        f.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    meta = destino / "draft_meta_info.json"
    if meta.exists():
        data = json.loads(meta.read_text(encoding="utf-8"))
        for grupo in data.get("draft_materials", []):
            for it in grupo.get("value", []):
                x = largos.get(Path(it.get("file_Path", "")).name)
                if x and grupo.get("type") == 0:
                    it["file_Path"] = x[0]
                    it["duration"] = max(it.get("duration") or 0, x[1] or 0)
                    cambios += 1
        meta.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return cambios


def cmd_materiales(a):
    """Proyecto ya montado (y quizá tocado a mano): cada clip pasa a usar el vídeo original entero,
    sin mover ni un corte, para poder alargarlos en CapCut."""
    d = TRABAJO / a.pieza
    destino = Path(a.proyecto)
    if not destino.exists():
        destino = carpeta_borradores() / a.proyecto
    if not destino.exists():
        sys.exit(f"No encuentro el proyecto de CapCut «{a.proyecto}».")
    if capcut_abierto():
        sys.exit("CapCut está abierto: ciérralo y vuelve a lanzarlo (no se ha escrito nada).")
    originales = {Path(t["video"]).name: t["video"] for t in leer_json(d / "transcripciones.json")}
    cc, env = capcut_bin(), entorno_capcut()
    info = destino / "draft_info.json" if (destino / "draft_info.json").exists() else destino

    def segmentos_de():
        r = subprocess.run([cc, "segments", str(info)], capture_output=True, text=True, check=True)
        return [x for x in json.loads(r.stdout) if x["type"] == "video"]

    antes = segmentos_de()
    copia = d / "backups" / f"{destino.name}-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copytree(destino, copia, ignore=shutil.ignore_patterns(".locked"))
    for seg in antes:
        if seg["label"] not in originales:
            print(f"  {seg['label']}: no es de esta pieza, se deja")
            continue
        subprocess.run([cc, "replace-media", str(info), seg["id"], originales[seg["label"]], "-q"],
                       check=True, env=env, stderr=subprocess.DEVNULL)
    if (destino / "Timelines").is_dir():  # CapCut 9.5 recarga de Timelines/<id>/: hay que copiarlo allí
        subprocess.run([cc, "sync-timelines", str(destino), "--nested", "--apply"],
                       check=True, capture_output=True)
    apuntar_originales(destino, originales)
    despues = segmentos_de()
    igual = [(x["start_us"], x["duration_us"]) for x in antes] == [(x["start_us"], x["duration_us"]) for x in despues]
    print(f"{len(antes)} clips con el vídeo entero · cortes {'idénticos' if igual else 'CAMBIADOS (ver copia)'} · copia: {copia}")
    if not igual:
        sys.exit(1)


# ---------------------------------------------------------------- fase 2: subtítulos

CORTAS = {"a", "al", "de", "del", "el", "la", "las", "lo", "los", "en", "y", "o", "que", "se", "un",
          "una", "por", "con", "no", "me", "te", "le", "mi", "tu", "su", "es", "i", "els", "les", "amb"}
NO_CLAVE = CORTAS | {"para", "como", "todo", "todos", "mucho", "más", "aquí", "este", "esto", "esta",
                     "pero", "porque", "tener", "tenemos", "favor", "seguro", "vale", "pues", "donde"}
ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "al", "del", "de", "en", "con", "por",
             "para", "a", "sin", "sobre", "els", "les", "amb", "per"}  # van pegados a la palabra que sigue
CUE_MIN = 0.25
SEG_PEGADO = 0.15


def palabras_en_timeline(d, trans, frases, proyecto):
    """Palabras con su tiempo en el timeline REAL del proyecto (Gerard puede haber movido cortes):
    cada clip de vídeo de CapCut -> las palabras de su tramo de origen, sin volver a transcribir."""
    info = proyecto / "draft_info.json" if (proyecto / "draft_info.json").exists() else proyecto
    r = subprocess.run([capcut_bin(), "segments", str(info)], capture_output=True, text=True, check=True)
    por_nombre = {Path(t["video"]).name: vi for vi, t in enumerate(trans)}
    frase_de = {}
    for f in frases:
        if f["queda"]:
            fuera = set(f["quitar_palabras"])
            for k, w in enumerate(f["palabras"]):
                if k not in fuera:
                    frase_de[(f["video"], w["s"])] = f["id"]
    # las copias de la rotoscopia (pistas "-copy") son el mismo vídeo: no cuentan para las palabras
    copias = {seg["id"] for t in json.loads(info.read_text(encoding="utf-8")).get("tracks", [])
              if "-copy" in (t.get("name") or "") for seg in t.get("segments", [])}
    out, envs = [], {}
    for seg in json.loads(r.stdout):
        if seg["type"] != "video" or seg["label"] not in por_nombre or seg["id"] in copias:
            continue
        r2 = subprocess.run([capcut_bin(), "segment", str(info), seg["id"]], capture_output=True, text=True, check=True)
        x = json.loads(r2.stdout)
        src = (x.get("segment") or x)["source_timerange"]
        s0, s1 = src["start"] / 1e6, (src["start"] + src["duration"]) / 1e6
        t0 = seg["start_us"] / 1e6
        vi = por_nombre[seg["label"]]
        env = envs.setdefault(vi, envolvente(trans[vi]["video"]))
        prev_e = 0.0
        for w in trans[vi]["palabras"]:
            medio = (w["s"] + w["e"]) / 2
            # Whisper da el inicio tarde (mediana 90 ms): tras una pausa, el bloque sale con el sonido
            ini = borde_sonido(env, w["s"], -1, 0.3, quieto=0.03)
            ini = ini if ini is not None and ini > prev_e else w["s"]
            prev_e = w["e"]
            if s0 <= medio <= s1 and (vi, w["s"]) in frase_de:
                out.append({"w": w["w"], "ts": round(t0 + max(ini, s0) - s0, 3),
                            "te": round(t0 + min(w["e"], s1) - s0, 3), "frase": frase_de[(vi, w["s"])],
                            "fin_clip": round(t0 + s1 - s0, 3)})
    return sorted(out, key=lambda w: w["ts"])


def limpiar(txt, fixes):
    t = re.sub(r"[.,;:!?¿¡\"«»]", "", txt).strip()
    return fixes.get(t.lower(), fixes.get(t, t))


def construir_cues(palabras, estilo, ajustes):
    """Bloques de 1-2 palabras sin partir palabras; las cortas van con la siguiente."""
    fixes = {k.lower(): v for k, v in cargar_vocabulario()[1].items()}
    fixes.update({k.lower(): v for k, v in ajustes.get("correcciones", {}).items()})
    n = estilo.get("palabras_por_bloque", 1)
    cues, i = [], 0
    while i < len(palabras):
        grupo = [palabras[i]]
        while (len(grupo) < n or grupo[-1]["te"] - grupo[0]["ts"] < CUE_MIN) and i + 1 < len(palabras) \
                and palabras[i + 1]["frase"] == grupo[0]["frase"] \
                and (len(grupo) < n or norm(grupo[-1]["w"]) in CORTAS or grupo[-1]["te"] - grupo[0]["ts"] < CUE_MIN) \
                and len(grupo) < max(n, 2):
            i += 1
            grupo.append(palabras[i])
        if n >= 2 and norm(grupo[-1]["w"]) in CORTAS and i + 1 < len(palabras) and len(grupo) > 1:
            i -= 1
            grupo.pop()  # "de" al final del bloque: mejor empieza el siguiente
        txt = " ".join(limpiar(w["w"], fixes) for w in grupo)
        txt = txt.upper() if estilo.get("mayusculas") else txt.lower()
        cues.append({"ini": grupo[0]["ts"], "fin": grupo[-1]["te"], "texto": txt,
                     "frase": grupo[0]["frase"], "fin_clip": grupo[-1]["fin_clip"]})
        i += 1
    for a, b in zip(cues, cues[1:]):  # sin parpadeo entre bloques seguidos
        if b["ini"] - a["fin"] < SEG_PEGADO:
            a["fin"] = b["ini"]
    for c in cues:
        c["fin"] = min(max(c["fin"], c["ini"] + CUE_MIN), c["fin_clip"]) if c["fin_clip"] - c["ini"] >= CUE_MIN \
            else max(c["fin"], c["ini"] + CUE_MIN)
    for a, b in zip(cues, cues[1:]):
        a["fin"] = min(a["fin"], b["ini"])
    return cues, fixes


def colores_de(ws, colores):
    """Índice de palabra -> color, si nombra uno ("nogal oscuro" colorea las dos palabras)."""
    if not colores:
        return {}
    cn = {" ".join(norm(x) for x in k.split()): v for k, v in colores.items()}
    out, j = {}, 0
    while j < len(ws):
        dos = " ".join(norm(w["w"]) for w in ws[j:j + 2])
        if j + 1 < len(ws) and dos in cn:
            out[j] = out[j + 1] = cn[dos]
            j += 2
            continue
        if norm(ws[j]["w"]) in cn:
            out[j] = cn[norm(ws[j]["w"])]
        j += 1
    return out


def construir_titulares(palabras, estilo, ajustes, fixes, colores=None):
    """Un titular por idea (cada trozo de frase hasta coma/punto/pausa, si tiene una palabra que
    lo merezca): mejor de más, Gerard borra los que sobran. Cada palabra en su línea, salvo
    artículo/preposición + palabra, que van juntos ("los RINCONES"); la clave en mayúsculas y
    grande, el resto pequeño. Cada línea entra cuando se dice y todas salen juntas."""
    trozos, act = [], []
    for k, w in enumerate(palabras):
        if act and (w["frase"] != act[-1]["frase"] or w["ts"] - act[-1]["te"] > 0.3):
            trozos.append(act)
            act = []
        act.append(w)
        if w["w"].endswith((",", ".", "?", "!")):
            trozos.append(act)
            act = []
    if act:
        trozos.append(act)
    manuales = {fid: [norm(x) for x in (v if isinstance(v, list) else [v])]
                for fid, v in ajustes.get("claves", {}).items()}
    usadas, tit = set(), []
    for ws in trozos:
        fid = ws[0]["frase"]
        if manuales.get(fid) == [""]:
            continue
        # claves a mano: un titular por cada una (varias por frase larga); si no, la más larga
        claves = [k for k, w in enumerate(ws) if norm(w["w"]) in manuales.get(fid, [])]
        if not claves:
            cands = [k for k, w in enumerate(ws) if norm(w["w"]) not in NO_CLAVE | usadas and len(norm(w["w"])) >= 5]
            claves = [max(cands, key=lambda j: len(norm(ws[j]["w"])))] if cands else []
        col = colores_de(ws, colores)
        desde = 0
        for k in claves:
            usadas.add(norm(ws[k]["w"]))
            t = titular(ws, k, desde, col, estilo, fixes, fid)
            desde = k + 1
            tit.append(t)
    for t, sig in zip(tit, tit[1:]):  # no se pisan: el siguiente titular echa al anterior
        t["fin"] = min(t["fin"], sig["ini"])
    return tit


def titular(ws, k, desde, col, estilo, fixes, fid):
    if True:
        hasta = k + 1
        while hasta - k <= 3 and (hasta in col or (hasta + 1 in col and norm(ws[hasta]["w"]) in CORTAS)):
            hasta += 1  # "tiradores grafito", "encimera en gris": el color se dice y entra en el titular
        sel = ws[max(desde, k - estilo.get("palabras_antes", 3)):hasta]
        # "de plástico": si la clave cierra con un artículo/preposición delante, va con ella
        lineas, pend = [], []
        for j, w in enumerate(sel):
            txt = limpiar(w["w"], fixes)
            es_clave = w is ws[k]
            if norm(w["w"]) in ARTICULOS and not es_clave and j + 1 < len(sel):
                pend.append((txt.lower(), w))
                continue
            menor = " ".join(t for t, _ in pend)
            ini = pend[0][1]["ts"] if pend else w["ts"]
            pal = txt.upper() if es_clave else txt.lower()
            color = col.get(ws.index(w))
            lineas.append({"ini": ini, "menor": menor, "texto": pal, "clave": es_clave, "color": color})
            pend = []
        fin = max(ws[-1]["te"], lineas[-1]["ini"] + 0.8) + estilo.get("salida_extra", 0.25)
        return {"frase": fid, "ini": lineas[0]["ini"], "fin": fin, "lineas": lineas}


def srt(cues, campo="texto"):
    def t(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "".join(f"{k}\n{t(c['ini'])} --> {t(c['fin'])}\n{c[campo]}\n\n"
                   for k, c in enumerate(cues, 1) if c[campo])


def preset_de(e, ruta, x=None, y=None, color=None, rangos=None):
    """Preset de capcut-cli con todo el estilo (fuente incluida, que no tiene otra vía)."""
    fuente = AQUI / e["archivo_fuente"] if e.get("archivo_fuente") else None
    if fuente:
        instalada = (Path.home() / "Library/Fonts" if sys.platform == "darwin" else
                     Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts") / fuente.name
        fuente = instalada if instalada.exists() else (fuente if fuente.exists() else None)
    style = {"text_color": color or e["color"], "font_size": e["tamano"], "bold": bool(e.get("negrita")),
             "letter_spacing": e.get("espaciado", 0)}
    sombra = e.get("sombra")
    if isinstance(sombra, dict):
        style.update(has_shadow=True, shadow_color=sombra["color"], shadow_alpha=sombra["alpha"],
                     shadow_distance=sombra["distancia"], shadow_smoothing=sombra["difuminado"],
                     shadow_angle=sombra["angulo"])
    elif sombra:
        style.update(has_shadow=True, shadow_alpha=0.6)
    if e.get("borde"):
        style.update(has_border=True, border_width=e["borde"], border_color="#000000")
    if fuente:
        style.update(font_path=str(fuente), font_name=e["fuente"])
    preset = {"capcutCliPreset": 1, "style": style}
    if x is not None:
        preset["transform"] = {"x": x, "y": y}
    if rangos:
        preset["text_ranges"] = rangos
    escribir_json(ruta, preset)


def poner_subtitulos(info, cues, e, d):
    """Pista de subtítulos de verdad (la de `capcut caption`: sub_type 1), con nuestros tiempos
    por palabra y nuestro texto; sin Whisper ni nube."""
    palabras, lineas = [], []
    for c in cues:
        ws = c["texto"].split()
        paso = (c["fin"] - c["ini"]) / len(ws)
        palabras += [{"word": w, "start": round(c["ini"] + k * paso, 3), "end": round(c["ini"] + (k + 1) * paso, 3)}
                     for k, w in enumerate(ws)]
        lineas.append(c["texto"])
    escribir_json(d / "subtitulos-palabras.json", palabras)
    (d / "subtitulos-guion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    preset_de(e, d / "preset-Subtitulos.json", e.get("x", 0), e.get("y", 0))
    r = subprocess.run([capcut_bin(), "caption", str(info), "--words", str(d / "subtitulos-palabras.json"),
                        "--script", str(d / "subtitulos-guion.txt"), "--track-name", "Subtitulos",
                        "--preset", str(d / "preset-Subtitulos.json")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("capcut caption ha fallado: " + (r.stdout + r.stderr)[-800:])
    return json.loads(r.stdout.splitlines()[0])["cues"]


def colocar_pista(destino, pista, x, y):
    """`capcut caption` deja los subtítulos siempre en y=-0.6 y no hay comando para moverlos:
    se cambia solo la posición de esa pista en todas las copias que lee CapCut."""
    mirrors = [f for patron in ("draft_info.json", "draft_content.json", "template-2.tmp")
               for f in [destino / patron, *destino.glob(f"Timelines/*/{patron}")] if f.exists()]
    for f in mirrors:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for t in data.get("tracks", []):
            if t.get("type") == "text" and t.get("name") == pista:
                for seg in t.get("segments", []):
                    seg.setdefault("clip", {}).setdefault("transform", {}).update(x=x, y=y)
        f.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


PX_POR_UNIDAD = 2.8  # px de alto por unidad de tamaño de CapCut en 1920 (calibrar con lo que diga Gerard)
ANCHO_SEGURO = 0.86  # fracción del ancho que puede ocupar un texto sin que lo corte el borde


def ruta_fuente(est):
    f = AQUI / est.get("archivo_fuente", "")
    return f if est.get("archivo_fuente") and f.exists() else None


def ancho(est, texto, tamano):
    """Ancho del texto en fracción del ancho del vídeo (1080), medido con la fuente de verdad."""
    px = tamano * PX_POR_UNIDAD
    f = ruta_fuente(est)
    try:
        from PIL import ImageFont
        if f:
            return ImageFont.truetype(str(f), int(px)).getlength(texto) / 1080
    except ImportError:
        pass
    return len(texto) * px * 0.6 / 1080


def alto_linea(tamano):
    return tamano * PX_POR_UNIDAD * 1.25 / 960  # en unidades de CapCut (media pantalla = 1)


def maquetar(t, e, x=0.0, ancho_max=ANCHO_SEGURO):
    """Tamaños de cada línea (encogiendo solo si no cabe) y su caja (x0, y0, x1, y1 en 0..1)."""
    lineas, alto_total, w_max = [], 0, 0
    for ln in t["lineas"]:
        est = e["clave"] if ln["clave"] else e["menor"]
        txt = f"{ln['menor']} {ln['texto']}".strip()
        tam = est["tamano"]
        while tam > est["tamano"] * 0.5 and ancho(est, txt, tam) > ancho_max:
            tam -= 1
        lineas.append(tam)
        alto_total += alto_linea(tam) + e.get("hueco", 0.015)
        w_max = max(w_max, ancho(est, txt, tam))
    cx = (1 + x) / 2
    return lineas, (cx - w_max / 2, (1 - e["y"]) / 2, cx + w_max / 2, (1 - (e["y"] - alto_total)) / 2)


def zonas_sin_cara(info, tit, e, d):
    """Todos los titulares en la misma zona (entre el primer y el segundo tercio). Si tapan una cara
    (OpenCV, un fotograma cada 0,3 s), se mueven de lado dentro de la zona, nunca abajo."""
    caras_por = [[] for _ in tit]
    try:
        import cv2
        proxy = d / "proxy-caras.mp4"
        subprocess.run([capcut_bin(), "render", str(info), "--out", str(proxy), "--scale", "0.5",
                        "--ffmpeg-cmd", ffmpeg_bin()], capture_output=True)
        cap = cv2.VideoCapture(str(proxy))
        fr = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        pf = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
        for i, t in enumerate(tit):
            n = max(3, int((t["fin"] - t["ini"]) / 0.3))
            for k in range(n):
                cap.set(cv2.CAP_PROP_POS_MSEC, (t["ini"] + k / (n - 1) * (t["fin"] - t["ini"]) * 0.98) * 1000)
                ok, img = cap.read()
                if not ok:
                    continue
                g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                h, w = g.shape
                for det in (fr, pf):
                    for (x, y, cw, ch) in det.detectMultiScale(g, 1.1, 5, minSize=(w // 22, w // 22)):
                        m = 0.15
                        caras_por[i].append(((x - m * cw) / w, (y - m * ch) / h, (x + cw * (1 + m)) / w, (y + ch * (1 + m)) / h))
    except (ImportError, AttributeError):
        pass
    movidos = 0
    for t, caras in zip(tit, caras_por):
        for x, amax in ((0.0, ANCHO_SEGURO), (-0.45, 0.5), (0.45, 0.5)):
            tams, bx = maquetar(t, e, x, amax)
            if not any(bx[0] < c[2] and c[0] < bx[2] and bx[1] < c[3] and c[1] < bx[3] for c in caras):
                break
        else:
            x, (tams, bx) = 0.0, maquetar(t, e, 0.0)  # sin hueco libre: centrado (Gerard decide)
        t["x"], t["tamanos"] = x, tams
        movidos += x != 0.0
    return movidos


def exclamaciones(palabras, estilo):
    """"por favor", "ojo", "nunca"... (lista editable en el estilo) -> texto enorme detrás del sujeto."""
    lista = [[norm(x) for x in f.split()] for f in estilo.get("exclamaciones", [])]
    toks = [norm(w["w"]) for w in palabras]
    out, k = [], 0
    while k < len(palabras):
        for f in sorted(lista, key=len, reverse=True):
            if toks[k:k + len(f)] == f:
                ws = palabras[k:k + len(f)]
                out.append({"ini": ws[0]["ts"], "fin": round(ws[-1]["te"] + 0.25, 3),
                            "texto": " ".join(limpiar(w["w"], {}) for w in ws).upper()})
                k += len(f) - 1
                break
        else:
            if palabras[k]["w"].startswith("¡"):
                pass
        k += 1
    return out


def mirrors_de(destino):
    return [f for patron in ("draft_info.json", "draft_content.json", "template-2.tmp")
            for f in [destino / patron, *destino.glob(f"Timelines/*/{patron}")] if f.exists()]


def editar_mirrors(destino, cambio):
    """Aplica `cambio(data)` a todas las copias del timeline que lee CapCut (raíz + Timelines/<id>/)."""
    for f in mirrors_de(destino):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        cambio(data)
        f.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def a_formato_subtitulo(destino, pista, idioma="es-ES"):
    """Convierte la pista en subtítulos de CapCut como los automáticos (muestra de Gerard 30/10):
    material type "subtitle" con words/recognize_text, un group_id común (es lo que hace que al
    mover o cambiar uno cambien todos) y la pista con flag 1."""
    grupo = f"Auto_{int(time.time() * 1000)}"

    def cambio(data):
        mats = {m["id"]: m for m in data.get("materials", {}).get("texts", [])}
        for t in data.get("tracks", []):
            if t.get("type") != "text" or t.get("name") != pista:
                continue
            t["flag"] = 1
            for seg in t.get("segments", []):
                m = mats.get(seg["material_id"])
                if not m:
                    continue
                txt = json.loads(m["content"])["text"] if m.get("content", "").startswith("{") else ""
                ws = txt.split()
                dur = seg["target_timerange"]["duration"] // 1000
                paso = dur // max(len(ws), 1)
                m.update(type="subtitle", sub_type=0, add_type=1, recognize_type=0, group_id=grupo,
                         recognize_text=txt, language=idioma, check_flag=7,
                         words=json.dumps({"start_time": [k * paso for k in range(len(ws))],
                                           "end_time": [(k + 1) * paso for k in range(len(ws))], "text": ws}),
                         current_words={"start_time": [], "end_time": [], "text": []})
                seg["source_timerange"] = None
                seg["render_index"] = 15001  # como los automáticos de CapCut
    editar_mirrors(destino, cambio)


def poner_titulares(info, tit, e, d):
    """Cada línea es su propio texto: entra con su palabra, todas salen a la vez."""
    cc, n = capcut_bin(), 0
    for t in tit:
        y = e["y"]
        tams = t.get("tamanos") or maquetar(t, e)[0]
        for k, (ln, tam) in enumerate(zip(t["lineas"], tams)):
            est = dict(e["clave"] if ln["clave"] else e["menor"], tamano=tam)
            texto = f"{ln['menor']} {ln['texto']}".strip()
            rangos = None
            if ln["menor"] and ln["clave"]:  # "los RINCONES": el artículo pequeño, en la misma línea
                rangos = [{"start": 0, "end": len(ln["menor"]), "font_size": round(tam * e["menor"]["tamano"] / e["clave"]["tamano"])}]
            alto = alto_linea(tam)
            y -= alto / 2
            preset = d / "preset-titular.json"
            preset_de(est, preset, t.get("x", 0.0), round(y, 4), ln["color"], rangos)
            subprocess.run([cc, "add-text", str(info), str(round(ln["ini"], 3)), str(round(t["fin"] - ln["ini"], 3)),
                            texto, "--track-name", f"Titulares {k + 1}", "--preset", str(preset), "--align", "1"],
                           capture_output=True, text=True, check=True)
            y -= alto / 2 + e.get("hueco", 0.015)
            n += 1
    return n


def poner_exclamaciones(info, exc, e, d):
    """Texto enorme centrado + copia del clip recortada a la exclamación, muda y con el fondo quitado
    (rotoscopia: el sujeto queda delante del texto). El orden de capas se fija luego en ordenar_recortes."""
    cc = capcut_bin()
    clips = [x for x in json.loads(subprocess.run([cc, "segments", str(info)], capture_output=True, text=True,
                                                    check=True).stdout) if x["type"] == "video"]
    for x in exc:
        tam = e["tamano"]
        while tam > 20 and ancho(e, x["texto"], tam) > 0.95:
            tam -= 1
        preset = d / "preset-exclamacion.json"
        preset_de(dict(e, tamano=tam), preset, 0.0, e.get("y", 0.2))
        r = subprocess.run([cc, "add-text", str(info), str(x["ini"]), str(round(x["fin"] - x["ini"], 3)), x["texto"],
                            "--track-name", "Exclamaciones", "--preset", str(preset), "--align", "1"],
                           capture_output=True, text=True, check=True)
        tid = json.loads(r.stdout.splitlines()[0])["segment_id"]
        for t, v in ((0, 0.92), (round(x["fin"] - x["ini"], 3), 1.06)):  # entra y crece un poco
            subprocess.run([cc, "keyframe", str(info), tid, "scale", str(t), str(v)], capture_output=True)
        base = next((c for c in clips if c["start_us"] <= x["ini"] * 1e6 < c["start_us"] + c["duration_us"]), None)
        if not base:
            continue
        r = subprocess.run([cc, "duplicate", str(info), base["id"], "--new-track"], capture_output=True, text=True, check=True)
        cid = json.loads(r.stdout.splitlines()[0])["new_segment_id"]
        seg = json.loads(subprocess.run([cc, "segment", str(info), base["id"]], capture_output=True, text=True,
                                        check=True).stdout)
        src0 = (seg.get("segment") or seg)["source_timerange"]["start"] / 1e6
        dentro = x["ini"] - base["start_us"] / 1e6
        dur = min(x["fin"], (base["start_us"] + base["duration_us"]) / 1e6) - x["ini"]
        subprocess.run([cc, "trim", str(info), cid, str(round(src0 + dentro, 3)), str(round(dur, 3))], check=True, capture_output=True)
        subprocess.run([cc, "shift", str(info), cid, f"+{dentro:.3f}s"], check=True, capture_output=True)
        subprocess.run([cc, "volume", str(info), cid, "0"], check=True, capture_output=True)
        subprocess.run([cc, "matting", str(info), cid], check=True, capture_output=True)
        x["recorte"] = cid
    return exc


def ordenar_recortes(destino, exc):
    """Capas: vídeo, texto de la exclamación y, ENCIMA, la copia recortada del sujeto. CapCut pinta
    los textos por encima del vídeo (render_index 15000): la copia sube por encima de ese número."""
    ids = {x["recorte"] for x in exc if x.get("recorte")}

    def cambio(data):
        for t in data.get("tracks", []):
            for seg in t.get("segments", []):
                if seg["id"] in ids:
                    seg["render_index"] = 16000
                    seg["track_render_index"] = 99
        tracks = data.get("tracks", [])
        arriba = [t for t in tracks if any(seg["id"] in ids for seg in t.get("segments", []))]
        data["tracks"] = [t for t in tracks if t not in arriba] + arriba
    if ids:
        editar_mirrors(destino, cambio)


def cmd_subtitulos(a):
    d = TRABAJO / a.pieza
    trans = leer_json(d / "transcripciones.json")
    _, _, frases, _ = cargar_pieza(a.pieza)
    destino = Path(a.proyecto)
    if not destino.exists():
        destino = carpeta_borradores() / a.proyecto
    if not destino.exists():
        sys.exit(f"No encuentro el proyecto de CapCut «{a.proyecto}».")
    estilo = leer_json(AQUI / "estilos" / f"{a.estilo}.json")
    aj_f = d / "subtitulos.json"
    ajustes = leer_json(aj_f) if aj_f.exists() else {"correcciones": {}, "claves": {}}
    if not aj_f.exists():
        escribir_json(aj_f, ajustes)
    palabras = palabras_en_timeline(d, trans, frases, destino)
    cues, fixes = construir_cues(palabras, estilo["subtitulos"], ajustes)
    colores = estilo.get("colores") if estilo.get("colores_nombrados") else None
    tit = construir_titulares(palabras, estilo["titular"], ajustes, fixes, colores) if estilo.get("titular") else []
    exc = exclamaciones(palabras, estilo["exclamacion"]) if estilo.get("exclamacion") else []
    for t in tit:  # la exclamación manda: las líneas que caerían encima esperan a que acabe
        for x in exc:
            for ln in t["lineas"]:
                if x["ini"] - 0.05 <= ln["ini"] < x["fin"]:
                    ln["ini"] = x["fin"]
        t["ini"] = t["lineas"][0]["ini"]
    tit = [t for t in tit if t["fin"] - t["lineas"][-1]["ini"] >= 0.4]
    md = [f"# Subtítulos · {a.pieza} · estilo {a.estilo}", "",
          f"{len(cues)} bloques · {len(tit)} titulares. Correcciones y claves: `subtitulos.json` "
          "(\"claves\": {\"F003\": [\"palabra\", ...]} o \"\" para quitar los titulares de esa frase).", "",
          "## Titulares (cada línea entra con su palabra; salen todas juntas)", ""]
    for t in tit:
        md.append(f"- {t['frase']} · sale {tc(t['fin'])} · " + " / ".join(
            f"{tc(l['ini'])} {(l['menor'] + ' ' + l['texto']).strip()}" + (f" [{l['color']}]" if l["color"] else "")
            for l in t["lineas"]))
    md += ["", "## Exclamaciones (enormes, detrás del sujeto)", ""] + \
          [f"- {tc(x['ini'])}–{tc(x['fin'])} {x['texto']}" for x in exc]
    md += ["", "## Bloques", ""] + [f"- {tc(c['ini'])}–{tc(c['fin'])} {c['texto']}" for c in cues]
    (d / "subtitulos.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    escribir_json(d / "subtitulos-cues.json", {"cues": cues, "titulares": tit})
    print(f"{len(cues)} bloques, {len(tit)} titulares → {d / 'subtitulos.md'}")
    if a.solo_md:
        return
    if capcut_abierto():
        sys.exit("CapCut está abierto: ciérralo y vuelve a lanzarlo (no se ha escrito nada).")
    info = destino / "draft_info.json" if (destino / "draft_info.json").exists() else destino
    # las pistas de precapcut se reconocen por el nombre; las de Gerard (sin nombre) no se tocan
    data = json.loads(info.read_text(encoding="utf-8"))
    nuestras = [seg["id"] for t in data.get("tracks", [])
                if (t["type"] == "text" and (t.get("name") or "").startswith(("Subtitulos", "Titulares", "Exclamaciones")))
                or (t["type"] == "video" and "-copy" in (t.get("name") or ""))
                for seg in t.get("segments", [])]
    if nuestras and not a.rehacer:
        sys.exit("El proyecto ya tiene textos de precapcut: --rehacer los quita y los vuelve a poner.")
    copia = d / "backups" / f"{destino.name}-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copytree(destino, copia, ignore=shutil.ignore_patterns(".locked"))
    for sid in nuestras:
        subprocess.run([capcut_bin(), "remove", str(info), sid, "-q"], check=True, capture_output=True)
    # solo se AÑADEN pistas de texto: los cortes de vídeo no se tocan
    n = poner_subtitulos(info, cues, estilo["subtitulos"], d)
    if tit:
        print(f"  titulares movidos de lado para no tapar una cara: {zonas_sin_cara(info, tit, estilo['titular'], d)}")
        escribir_json(d / "subtitulos-cues.json", {"cues": cues, "titulares": tit})
    nl = poner_titulares(info, tit, estilo["titular"], d) if tit else 0
    if exc:
        poner_exclamaciones(info, exc, estilo["exclamacion"], d)
    if (destino / "Timelines").is_dir():
        subprocess.run([capcut_bin(), "sync-timelines", str(destino), "--nested", "--apply"],
                       check=True, capture_output=True)
    colocar_pista(destino, "Subtitulos", estilo["subtitulos"].get("x", 0), estilo["subtitulos"].get("y", 0))
    a_formato_subtitulo(destino, "Subtitulos", estilo.get("idioma", "es-ES"))
    ordenar_recortes(destino, exc)
    print(f"Añadidos {n} subtítulos, {len(tit)} titulares ({nl} líneas) y {len(exc)} exclamaciones · copia: {copia}")


def cmd_qa(a):
    """Re-transcribe el preview y lo compara con lo que debía quedar: palabras comidas o sobrantes."""
    d, trans, frases, tramos = cargar_pieza(a.pieza)
    prev = d / "preview.mp4"
    if not prev.exists():
        sys.exit("Primero `montar`.")
    esperado = [norm(w["w"]) for tr in tramos for w in tr["palabras"]]
    idioma = trans[0].get("idioma")
    r = transcribir(prev, idioma, a.modelo, d / "cache")
    oido = [norm(w["w"]) for w in r["palabras"]]
    sm = difflib.SequenceMatcher(None, esperado, oido, autojunk=False)
    problemas = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        t = r["palabras"][min(j1, len(r["palabras"]) - 1)]["s"] if r["palabras"] else 0
        problemas.append(f"- {tc(t)} · esperado «{' '.join(esperado[i1:i2])}» · se oye «{' '.join(oido[j1:j2])}»")
    # re-transcribir no ve una sílaba comida ("-sí" se sigue leyendo "así"): se mide el audio
    envs = [envolvente(t["video"]) for t in trans]
    bordes = []
    for k, tr in enumerate(tramos, 1):
        env = envs[tr["video"]]
        for lado, t in (("entra", tr["ini"]), ("sale", tr["fin"])):
            if nivel(env, t) >= env[1]:
                bordes.append(f"- corte {k} {lado} con sonido ({nivel(env, t):.0f} dB, umbral "
                              f"{env[1]:.0f}) · {Path(trans[tr['video']]['video']).name} {tc(t)}")
    txt = [f"# QA fase 1 · {a.pieza}", "",
           f"Coincidencia texto esperado/oído: {sm.ratio():.0%} ({len(esperado)} palabras).", "",
           "Bordes que cortan sonido (posible sílaba comida):", ""] + (bordes or ["- ninguno"]) + ["",
           "Diferencias (muchas son lecturas distintas del reconocedor, no cortes malos; "
           "revisa las que caen en un borde de corte):", ""] + (problemas or ["- ninguna"])
    (d / "qa-fase1.md").write_text("\n".join(txt) + "\n", encoding="utf-8")
    print(f"QA: {sm.ratio():.0%} · {len(problemas)} diferencias · {len(bordes)} bordes con sonido → {d / 'qa-fase1.md'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f1 = sub.add_parser("fase1", help="transcribir y decidir qué se queda")
    f1.add_argument("pieza")
    f1.add_argument("videos", nargs="+")
    f1.add_argument("--idioma", default=None, help="ca, es... (sin poner: lo detecta)")
    f1.add_argument("--modelo", default="medium")
    m = sub.add_parser("montar", help="preview + proyecto de CapCut")
    m.add_argument("pieza")
    m.add_argument("--en", help="proyecto de CapCut vacío (nombre o ruta) donde montar")
    m.add_argument("--nuevo", help="nombre del proyecto nuevo (por defecto, el de la pieza)")
    m.add_argument("--sin-capcut", action="store_true", help="solo preview y EDL")
    mt = sub.add_parser("materiales", help="clips con el vídeo original entero (para alargar en CapCut)")
    mt.add_argument("pieza")
    mt.add_argument("proyecto", help="proyecto de CapCut (nombre o ruta)")
    st = sub.add_parser("subtitulos", help="fase 2: añade pistas de subtítulos y titulares al proyecto")
    st.add_argument("pieza")
    st.add_argument("proyecto", help="proyecto de CapCut (nombre o ruta)")
    st.add_argument("--estilo", required=True, help="estilos/<cliente>.json")
    st.add_argument("--solo-md", action="store_true", help="solo subtitulos.md, sin tocar CapCut")
    st.add_argument("--rehacer", action="store_true", help="quita las pistas de texto de precapcut y las vuelve a poner")
    q = sub.add_parser("qa", help="re-transcribe el preview y busca palabras comidas")
    q.add_argument("pieza")
    q.add_argument("--modelo", default="small")
    a = p.parse_args()
    {"fase1": cmd_fase1, "montar": cmd_montar, "materiales": cmd_materiales, "subtitulos": cmd_subtitulos, "qa": cmd_qa}[a.cmd](a)


if __name__ == "__main__":
    main()
