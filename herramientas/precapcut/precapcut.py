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
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TRABAJO = Path(os.environ.get("PRECAPCUT_TRABAJO", Path.home() / "rmagency" / "work" / "precapcut"))

# Ajustes de corte (segundos). Probados contra el QA de Aprenent fotografia R01:
# márgenes 80 ms delante / 150 ms detrás no se comen sílabas.
PAD_ANTES = 0.08
PAD_DESPUES = 0.15
PAUSA_MAX = 0.35      # pausa más larga que esto dentro de lo que se queda -> se recorta
GAP_FRASE = 0.55      # pausa que separa dos frases
VENTANA_TOMAS = 5     # cuántas frases hacia delante se busca la repetición
SIM_TOMA = 0.6        # parecido mínimo para considerar que es la misma frase repetida
SIM_ARRANQUE = 0.75   # parecido mínimo de un arranque en falso con el inicio de la frase buena


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
            if rot in (90, 270):
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

def transcribir(video, idioma, modelo, cache_dir):
    """Palabras con tiempos. Cachea por nombre+tamaño+fecha: re-ejecutar no repite el trabajo."""
    st = Path(video).stat()
    clave = f"{Path(video).stem}-{st.st_size}-{int(st.st_mtime)}-{modelo}-{idioma or 'auto'}"
    cache = cache_dir / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', clave)}.json"
    if cache.exists():
        return leer_json(cache)

    from faster_whisper import WhisperModel
    pistas, fixes = cargar_vocabulario()
    print(f"  transcribiendo {Path(video).name} (modelo {modelo})...", flush=True)
    m = WhisperModel(modelo, device="auto", compute_type="int8")
    segs, info = m.transcribe(
        str(video),
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
            palabras.append({"w": txt, "s": round(w.start, 3), "e": round(w.end, 3),
                             "p": round(w.probability, 2)})
    data = {"video": str(Path(video).resolve()), "idioma": info.language, "palabras": palabras}
    escribir_json(cache, data)
    return data


# ---------------------------------------------------------------- análisis fase 1

MULETILLAS = {"eh", "ehm", "em", "emm", "mm", "mmm", "hmm", "uh", "um", "este", "eeh", "eee"}


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
        for j in range(i + 1, min(i + 1 + VENTANA_TOMAS, len(frases))):
            if frases[j]["video"] != f["video"] and j > i + 1:
                break
            b = [x for x in toks[j] if x and x not in MULETILLAS]
            if not b:
                continue
            completa = similitud(a, b)
            arranque = similitud(a, b[:len(a)]) if len(a) < len(b) else 0
            if len(a) >= 3 and completa >= SIM_TOMA:
                f["queda"], f["motivo"] = False, f"toma repetida (se queda {frases[j]['id']})"
                break
            if len(a) >= 1 and arranque >= SIM_ARRANQUE and len(b) - len(a) >= 2:
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


def segmentos(frases, transcripciones):
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
            ini = max(g[0]["s"] - PAD_ANTES, prev_e + 0.02, 0.0)
            fin = min(g[-1]["e"] + PAD_DESPUES, next_s - 0.02, dur)
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
    escribir_json(d / "decisiones.json", [
        {"id": f["id"], "queda": f["queda"], "motivo": f["motivo"],
         "quitar_palabras": f["quitar_palabras"],
         "texto": " ".join(w["w"] for w in f["palabras"])} for f in frases])
    tramos = segmentos(frases, trans)
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
    return d, trans, frases, segmentos(frases, trans)


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


def cmd_montar(a):
    d, trans, frases, tramos = cargar_pieza(a.pieza)
    escribir_json(d / "timeline.json", {"tramos": tramos, "videos": [t["video"] for t in trans]})
    with open(d / "edl.csv", "w", encoding="utf-8") as f:
        f.write("n,video,entrada,salida,linea_tiempo,texto\n")
        for k, tr in enumerate(tramos, 1):
            txt = " ".join(w["w"] for w in tr["palabras"]).replace('"', "'")
            f.write(f'{k},"{Path(trans[tr["video"]]["video"]).name}",{tr["ini"]},{tr["fin"]},{tr["tl"]},"{txt}"\n')
    print(f"{len(tramos)} tramos, {tc(sum(t['fin'] - t['ini'] for t in tramos))} en total")

    render_preview(trans, tramos, d / "preview.mp4")
    print(f"Preview: {d / 'preview.mp4'}")
    if a.sin_capcut:
        return

    if capcut_abierto():
        sys.exit("CapCut está abierto: ciérralo y vuelve a lanzar `montar` (no se ha escrito nada).")
    spec = spec_capcut(a.nuevo or a.pieza, trans, tramos)
    escribir_json(d / "spec-fase1.json", spec)
    cmd = [capcut_bin(), "compile", str(d / "spec-fase1.json")]
    if a.en:
        destino = Path(a.en)
        if not destino.exists():
            destino = carpeta_borradores() / a.en
        if not destino.exists():
            sys.exit(f"No encuentro el proyecto de CapCut «{a.en}».")
        copia = d / "backups" / destino.name
        if not copia.exists():
            shutil.copytree(destino, copia)
        cmd += ["--into", str(destino)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1500:] or r.stderr[-1500:])
    if r.returncode != 0:
        sys.exit("capcut compile ha fallado (ver arriba).")


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
    txt = [f"# QA fase 1 · {a.pieza}", "",
           f"Coincidencia texto esperado/oído: {sm.ratio():.0%} ({len(esperado)} palabras).", "",
           "Diferencias (muchas son lecturas distintas del reconocedor, no cortes malos; "
           "revisa las que caen en un borde de corte):", ""] + (problemas or ["- ninguna"])
    (d / "qa-fase1.md").write_text("\n".join(txt) + "\n", encoding="utf-8")
    print(f"QA: {sm.ratio():.0%} · {len(problemas)} diferencias → {d / 'qa-fase1.md'}")


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
    q = sub.add_parser("qa", help="re-transcribe el preview y busca palabras comidas")
    q.add_argument("pieza")
    q.add_argument("--modelo", default="small")
    a = p.parse_args()
    {"fase1": cmd_fase1, "montar": cmd_montar, "qa": cmd_qa}[a.cmd](a)


if __name__ == "__main__":
    main()
