"""Audio de cada pista del montaje final (en tiempo de arriba) -> faster-whisper con contexto."""
import sys, json, subprocess, numpy as np
sys.path.insert(0, '.')
import mapa, precapcut as p
from pathlib import Path
from faster_whisper import WhisperModel, decode_audio
SR = 16000
OUT = Path('retrans'); OUT.mkdir(exist_ok=True)
info = mapa.info; trans = mapa.trans
modelo = sys.argv[1] if len(sys.argv) > 1 else 'medium'
m = WhisperModel(modelo, device='auto', compute_type='int8')
prompt = ("Aprenent fotografia. Dia u, dia 2. Anem a la xixa. Un altre cop estem per aquí. "
          "Fotos, polígon, palets, pàdel, smash, l'Aleix, velocitat d'obturació, repipí, vídeo anterior.")
res = {}
for ci, (t0, c0, c1, dr, did) in enumerate(mapa.pistas()):
    vids = {mm['id']: mm['path'] for mm in dr['materials']['videos']}
    for ti, t in enumerate(dr['tracks']):
        segs = [s for s in t['segments'] if str(vids.get(s['material_id'], '')).lower().endswith('.mp4') and s.get('visible') is not False]
        if not segs: continue
        ini = min(s['target_timerange']['start'] for s in segs) / 1e6
        fin = max(s['target_timerange']['start'] + s['target_timerange']['duration'] for s in segs) / 1e6
        buf = np.zeros(int((fin - ini) * SR) + SR, dtype=np.float32)
        for s in segs:
            s0 = s['source_timerange']['start'] / 1e6; du = s['source_timerange']['duration'] / 1e6
            r = subprocess.run([p.ffmpeg_bin(), '-v', 'error', '-ss', f'{s0:.3f}', '-t', f'{du:.3f}', '-i', vids[s['material_id']],
                                '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True)
            a = np.frombuffer(r.stdout, dtype=np.float32)
            k = int((s['target_timerange']['start'] / 1e6 - ini) * SR)
            buf[k:k + len(a)] = a[:len(buf) - k]
        segs_w, _ = m.transcribe(buf, language='ca', word_timestamps=True, vad_filter=True,
                                 condition_on_previous_text=True, initial_prompt=prompt, beam_size=5)
        base = ini  # tiempo DENTRO del clip combinado
        ws = [{'w': w.word.strip(), 's': round(base + w.start, 3), 'e': round(base + w.end, 3), 'p': round(w.probability, 2)}
              for sg in segs_w for w in (sg.words or []) if w.word.strip()]
        res[f'{did},{ti}'] = ws
        print(ci, ti, len(ws), ' '.join(w['w'] for w in ws)[:3000], flush=True)
json.dump(res, open(OUT / f'interno-{modelo}.json', 'w'), ensure_ascii=False, indent=0)
