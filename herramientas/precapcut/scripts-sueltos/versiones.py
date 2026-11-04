"""Versiones (gancho + duración) como clips combinados nuevos, copiados de los de cada día."""
import json, copy, uuid, re, shutil, sys
from pathlib import Path
PROY = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft/Aprenent fotografia dia 1 i 2"
UUID = re.compile(r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$')
US = 1_000_000
D1, D2 = '848C66AF-68B3-4E5F-B446-6EDF03181C74', '8555D535-9B8E-47F3-9C90-F83CCB4749D3'
# gancho: (fuente del clip del gancho, pistas de texto del gancho [(índice, solo los que empiezan antes de s)])
G = {D1: {'tolls': ([801.70], [(5, 3)]), 'episodi': ([367.667], [(6, 99)])},
     D2: {'number one': ([466.667], [(7, 4.5), (10, 99)]), 'creatiu': ([385.70], [(8, 99)]), 'zoom': ([114.233], [(9, 99)])}}
VERSIONES = [
    (D1, 'D1 V1 tolls', 'tolls', []),
    (D1, 'D1 V2 episodi', 'episodi', [(18.47, 28.33), (59.23, 64.60), (89.13, 93.97)]),
    (D1, 'D1 V3 tolls curta', 'tolls', [(18.47, 28.33), (52.37, 64.60), (69.63, 73.63), (81.67, 110.20)]),
    (D2, 'D2 V1 number one', 'number one', []),
    (D2, 'D2 V2 creatiu', 'creatiu', [(24.70, 28.57), (68.83, 82.93), (122.93, 135.40)]),
    (D2, 'D2 V3 zoom curta', 'zoom', [(12.93, 16.27), (24.70, 28.57), (42.57, 48.23), (68.83, 82.93), (93.43, 101.53),
                                       (113.33, 135.40), (156.70, 161.53)]),
]

def nuevo(): return str(uuid.uuid4()).upper()

def ids_de(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'id' and isinstance(v, str) and UUID.match(v): out.add(v)
            ids_de(v, out)
    elif isinstance(o, list):
        for v in o: ids_de(v, out)
    return out

def remap(o, m):
    if isinstance(o, dict): return {k: remap(v, m) for k, v in o.items()}
    if isinstance(o, list): return [remap(v, m) for v in o]
    if isinstance(o, str):
        if o in m: return m[o]
        for a, b in m.items():
            if a in o and '/subdraft/' in o: o = o.replace(a, b)
        return o
    return o

def fin(s): return s['target_timerange']['start'] + s['target_timerange']['duration']

def gancho(inner, did, elegido):
    vids = {m['id']: m for m in inner['materials']['videos']}
    for nombre, (fuentes, textos) in G[did].items():
        for ti, t in enumerate(inner['tracks']):
            if t['type'] == 'video' and ti > 0:
                for s in list(t['segments']):
                    src = (s.get('source_timerange') or {}).get('start', 0) / US
                    if s['target_timerange']['start'] < 0.5 * US and any(abs(src - f) < 0.05 for f in fuentes) \
                            and str(vids.get(s['material_id'], {}).get('path', '')).lower().endswith('.mp4'):
                        if nombre == elegido: s['visible'] = True
                        else: t['segments'].remove(s)
        if nombre != elegido:
            for ti, hasta in textos:
                t = inner['tracks'][ti]
                t['segments'] = [s for s in t['segments'] if s['target_timerange']['start'] >= hasta * US]

def recortar(inner, rangos):
    for x, y in sorted(rangos, reverse=True):
        x, y = int(round(x * US)), int(round(y * US)); L = y - x
        for t in inner['tracks']:
            keep = []
            for s in t['segments']:
                tt = s['target_timerange']; a, b = tt['start'], fin(s); st = s.get('source_timerange')
                if t['type'] == 'text' and x <= (a + b) // 2 < y and not (a < x and b > y):
                    continue  # un texto con más de la mitad dentro del corte se va entero
                sp = s.get('speed', 1.0) or 1.0
                if b <= x: pass
                elif a >= y: tt['start'] = a - L
                elif a >= x and b <= y: continue
                elif a < x and b <= y:
                    tt['duration'] = x - a
                    if st: st['duration'] = int(round((x - a) * sp))
                elif a >= x and b > y:
                    c = y - a; tt['start'] = x; tt['duration'] = b - y
                    if st: st['start'] += int(round(c * sp)); st['duration'] = int(round((b - y) * sp))
                else:
                    tt['duration'] -= L
                    if st: st['duration'] = int(round(tt['duration'] * sp))
                keep.append(s)
            t['segments'] = keep
    inner['duration'] = max(fin(s) for t in inner['tracks'] for s in t['segments'])

def material(mats, mid):
    for k, v in mats.items():
        if isinstance(v, list):
            for m in v:
                if isinstance(m, dict) and m.get('id') == mid: return k, m
    return None, None

data = json.loads((PROY / 'draft_info.json').read_text())
mats = data['materials']; main = data['tracks'][0]
entradas = {e['id']: e for e in mats['drafts']}
segs = {next(r for r in s['extra_material_refs'] if r in entradas): s for s in main['segments']}
pos = max(fin(s) for s in main['segments'])
creadas = []
for did, nombre, elegido, rangos in VERSIONES:
    e0, s0 = entradas[did], segs[did]
    refs = [s0['material_id']] + s0['extra_material_refs']
    m = {i: nuevo() for i in ids_de(e0, set()) | set(refs) | {s0['id'], e0['combination_id']}}
    e = remap(copy.deepcopy(e0), m); inner = e['draft']
    inner['name'] = nombre
    gancho(inner, did, elegido); recortar(inner, rangos)
    dur = inner['duration']
    s = remap(copy.deepcopy(s0), m)
    s['target_timerange'] = {'start': pos, 'duration': dur}; s['source_timerange'] = {'start': 0, 'duration': dur}
    for r in refs:
        k, mm = material(mats, r)
        if k == 'drafts': continue
        mm = remap(copy.deepcopy(mm), m)
        if k == 'videos': mm['duration'] = dur; mm['material_name'] = nombre
        mats[k].append(mm)
    mats['drafts'].append(e); main['segments'].append(s)
    # carpeta subdraft (la que CapCut abre al entrar en el combinado)
    viejo = PROY / 'subdraft' / e0['draft']['id']; nueva = PROY / 'subdraft' / inner['id']
    if viejo.exists():
        if nueva.exists(): shutil.rmtree(nueva)
        shutil.copytree(viejo, nueva)
        w = remap(json.loads((viejo / 'draft_content.json').read_text()), m)
        for ee in w['materials'].get('drafts', []):
            if ee['id'] == e['id']: ee['draft'] = copy.deepcopy(inner)
        for t in w['tracks']:
            for ss in t['segments']:
                ss['target_timerange']['duration'] = dur; ss['source_timerange'] = {'start': 0, 'duration': dur}
        for v in w['materials'].get('videos', []):
            if v['id'] in m.values(): v['duration'] = dur
        w['duration'] = dur
        (nueva / 'draft_content.json').write_text(json.dumps(w, ensure_ascii=False, separators=(',', ':')))
        cfg = json.loads((viejo / 'sub_draft_config.json').read_text())
        cfg.update(id=inner['id'], project_id=inner['id'], name=nombre, rough_cut_duration=dur)
        (nueva / 'sub_draft_config.json').write_text(json.dumps(cfg, ensure_ascii=False))
    else:
        print('  sin carpeta subdraft para', nombre)
    creadas.append((nombre, pos / US, dur / US)); pos += dur
data['duration'] = pos
txt = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
for f in [PROY / 'draft_info.json', PROY / 'template-2.tmp', PROY / 'draft_content.json',
          *PROY.glob('Timelines/*/draft_info.json'), *PROY.glob('Timelines/*/template-2.tmp')]:
    if f.exists(): f.write_text(txt, encoding='utf-8')
for n, a, d in creadas: print(f'{n:22s} empieza {int(a//60)}:{a%60:05.2f}  dura {int(d//60)}:{d%60:05.2f}')
