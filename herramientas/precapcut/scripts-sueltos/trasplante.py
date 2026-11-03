import json, copy, glob
from pathlib import Path
import sys; sys.path.insert(0, '.')
import mapa
PROY = mapa.PROY
N = json.load(open('nuevos.json'))

def arreglar(data):
    mats = data['materials']
    # 1) fuera los subtítulos de arriba (los ponía precapcut; ahora van dentro)
    fuera = {s['material_id'] for t in data['tracks'] if t['type'] == 'text' and (t.get('name') or '').startswith('Subtitulos') for s in t['segments']}
    data['tracks'] = [t for t in data['tracks'] if not (t['type'] == 'text' and (t.get('name') or '').startswith('Subtitulos'))]
    mats['texts'] = [m for m in mats.get('texts', []) if m['id'] not in fuera]
    # 2) dentro de cada combinado: pistas nuevas + recorte al final del vídeo principal
    durs = {}
    for dr in mats.get('drafts', []):
        if dr['id'] not in N: continue
        inner = dr['draft']; tracks, texts = N[dr['id']]
        nombres = {t['name'] for t in tracks}
        viejos = {s['material_id'] for t in inner['tracks'] if t['type'] == 'text' and t.get('name') in nombres for s in t['segments']}
        inner['tracks'] = [t for t in inner['tracks'] if not (t['type'] == 'text' and t.get('name') in nombres)] + copy.deepcopy(tracks)
        inner['materials']['texts'] = [m for m in inner['materials'].get('texts', []) if m['id'] not in viejos] + copy.deepcopy(texts)
        fin = max(s['target_timerange']['start'] + s['target_timerange']['duration'] for s in inner['tracks'][0]['segments'])
        inner['duration'] = fin; durs[dr['id']] = fin
    # 3) los clips combinados de arriba, a su duración nueva y seguidos
    vid = {m['id']: m for m in mats.get('videos', [])}
    for t in data['tracks']:
        if t['type'] != 'video': continue
        pos = None
        for s in t['segments']:
            did = next((r for r in s.get('extra_material_refs', []) if r in durs), None)
            if not did: continue
            if pos is None: pos = s['target_timerange']['start']
            s['target_timerange'] = {'start': pos, 'duration': durs[did]}
            s['source_timerange'] = {'start': 0, 'duration': durs[did]}
            if s['material_id'] in vid: vid[s['material_id']]['duration'] = durs[did]
            pos += durs[did]
    if durs:
        data['duration'] = max(s['target_timerange']['start'] + s['target_timerange']['duration'] for t in data['tracks'] for s in t['segments'])
    return durs

base = json.loads((PROY / 'draft_info.json').read_text())
print('arriba', arreglar(base), base['duration'] / 1e6)
txt = json.dumps(base, ensure_ascii=False, separators=(',', ':'))
for f in [PROY / 'draft_info.json', PROY / 'draft_content.json', PROY / 'template-2.tmp',
          *PROY.glob('Timelines/*/draft_info.json'), *PROY.glob('Timelines/*/template-2.tmp')]:
    if f.exists(): f.write_text(txt, encoding='utf-8'); print('escrito', f.relative_to(PROY))
for f in PROY.glob('subdraft/*/draft_content.json'):
    d = json.loads(f.read_text()); r = arreglar(d)
    if r:
        f.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'); print('escrito', f.relative_to(PROY), r)
