"""En cada versión (D1…/D2…): música de Gerard (misma velocidad/volumen/inicio) a la duración del clip con
fundido final, y el título DIA N como textos sueltos (no subtítulo) en vez del clip combinado del título."""
import json, copy, uuid, glob
from pathlib import Path
PROY = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft/Aprenent fotografia dia 1 i 2"
US = 1_000_000; FADE = 1_500_000
def nuevo(): return str(uuid.uuid4()).upper()
def fin(s): return s['target_timerange']['start'] + s['target_timerange']['duration']

data = json.loads((PROY / 'draft_info.json').read_text())
mats = data['materials']
musica = next(t for t in data['tracks'] if t['type'] == 'audio')
mseg = musica['segments'][0]
mrefs = {}
for k, v in mats.items():
    if isinstance(v, list):
        for m in v:
            if isinstance(m, dict) and m.get('id') in mseg['extra_material_refs'] + [mseg['material_id']]: mrefs[m['id']] = (k, m)
titulos = {x['id']: x['draft'] for x in mats['drafts'] if not (x['draft'].get('name') or '')}

def poner_musica(inner):
    inner['tracks'] = [t for t in inner['tracks'] if not (t['type'] == 'audio' and t.get('name') == 'Musica')]
    dur = max(fin(s) for s in inner['tracks'][0]['segments'])
    m = {i: nuevo() for i in mrefs}
    s = copy.deepcopy(mseg); s['id'] = nuevo(); s['material_id'] = m[mseg['material_id']]
    s['extra_material_refs'] = [m[r] for r in mseg['extra_material_refs']]
    s['target_timerange'] = {'start': 0, 'duration': dur}
    s['source_timerange'] = {'start': mseg['source_timerange']['start'], 'duration': int(round(dur * mseg['speed']))}
    for old, (k, mm) in mrefs.items():
        c = copy.deepcopy(mm); c['id'] = m[old]; inner['materials'].setdefault(k, []).append(c)
    fid = nuevo()
    inner['materials'].setdefault('audio_fades', []).append(
        {'fade_in_duration': 0, 'fade_out_duration': FADE, 'fade_type': 0, 'id': fid, 'type': 'audio_fade'})
    s['extra_material_refs'].append(fid)
    t = copy.deepcopy(musica); t['id'] = nuevo(); t['name'] = 'Musica'; t['segments'] = [s]
    inner['tracks'].append(t)

def a_texto(m):
    m.update(type='text', group_id='', recognize_text='', add_type=0, sub_type=0, language='',
             words={'start_time': [], 'end_time': [], 'text': []}, current_words={'start_time': [], 'end_time': [], 'text': []})

def poner_titulo(inner):
    for ti, t in enumerate(list(inner['tracks'])):
        if t['type'] != 'video': continue
        for s in list(t['segments']):
            r = next((x for x in s.get('extra_material_refs', []) if x in titulos), None)
            if not r: continue
            tit = titulos[r]; a = s['target_timerange']['start']; src = (s.get('source_timerange') or {'start': 0})['start']
            d = s['target_timerange']['duration']
            txts = {m['id']: m for m in tit['materials'].get('texts', [])}
            for tt in tit['tracks']:
                if tt['type'] != 'text': continue
                nt = copy.deepcopy(tt); nt['id'] = nuevo(); nt['flag'] = 0; nt['segments'] = []
                for ts in tt['segments']:
                    i0 = max(ts['target_timerange']['start'], src); i1 = min(fin(ts), src + d)
                    if i1 <= i0: continue
                    ns = copy.deepcopy(ts); ns['id'] = nuevo()
                    ns['target_timerange'] = {'start': a + i0 - src, 'duration': i1 - i0}
                    mm = copy.deepcopy(txts[ts['material_id']]); mm['id'] = nuevo(); a_texto(mm)
                    ns['material_id'] = mm['id']; inner['materials'].setdefault('texts', []).append(mm)
                    nt['segments'].append(ns)
                txt = json.loads(txts[tt['segments'][0]['material_id']]['content'])['text'] if tt['segments'] else ''
                nt['name'] = f'Titol {txt}'
                if nt['segments']: inner['tracks'].append(nt)
            t['segments'].remove(s)

hechos = []
def arreglar(d):
    for x in d['materials'].get('drafts', []):
        inner = x['draft']
        if (inner.get('name') or '').startswith(('D1 ', 'D2 ')):
            poner_titulo(inner); poner_musica(inner); hechos.append(inner['name'])
arreglar(data)
print(sorted(hechos))
txt = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
for f in [PROY / 'draft_info.json', PROY / 'template-2.tmp', PROY / 'draft_content.json',
          *PROY.glob('Timelines/*/draft_info.json'), *PROY.glob('Timelines/*/template-2.tmp')]:
    if f.exists(): f.write_text(txt, encoding='utf-8')
nuevos = {x['id']: x['draft'] for x in data['materials']['drafts']}
for f in PROY.glob('subdraft/*/draft_content.json'):
    w = json.loads(f.read_text()); cambia = False
    for x in w['materials'].get('drafts', []):
        if x['id'] in nuevos and (nuevos[x['id']].get('name') or '').startswith(('D1 ', 'D2 ')):
            x['draft'] = copy.deepcopy(nuevos[x['id']]); cambia = True
    if cambia: f.write_text(json.dumps(w, ensure_ascii=False, separators=(',', ':'))); print('subdraft', f.parent.name)
