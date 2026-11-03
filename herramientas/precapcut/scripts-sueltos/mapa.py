"""Palabras del montaje de Gerard (clips combinados) en el timeline de arriba."""
import sys, json
sys.path.insert(0, '/Users/gerardruizmiro/rmagency/AGENTES RM/herramientas/precapcut')
import precapcut as p
from pathlib import Path
PROY = p.carpeta_borradores() / "Aprenent fotografia dia 1 i 2"
D = p.TRABAJO / 'aprenent-fotografia-dia01-02'
trans = p.leer_json(D / 'transcripciones.json')
frases = p.analizar(trans)
frase_de = {(f['video'], w['s']): f['id'] for f in frases for w in f['palabras']}
info = json.loads((PROY / 'draft_info.json').read_text())
drafts = {dr['id']: dr['draft'] for dr in info['materials']['drafts']}

def pistas():
    """[(t0_arriba, draft)] en orden"""
    out = []
    for s in info['tracks'][0]['segments']:
        did = next(r for r in s['extra_material_refs'] if r in drafts)
        out.append((s['target_timerange']['start'] / 1e6, s['source_timerange']['start'] / 1e6,
                    (s['source_timerange']['start'] + s['source_timerange']['duration']) / 1e6, drafts[did], did))
    return out

def palabras(solo_pista=None):
    """{indice_pista_interna: [palabras]} con ts/te arriba."""
    res = {}
    for ci, (t0, c0, c1, dr, did) in enumerate(pistas()):
        vids = {m['id']: m['path'].split('/')[-1] for m in dr['materials']['videos']}
        for ti, t in enumerate(dr['tracks']):
            for s in t['segments']:
                nombre = vids.get(s['material_id'])
                if not nombre or not nombre.lower().endswith('.mp4') or s.get('visible') is False:
                    continue
                vi = [Path(x['video']).name for x in trans].index(nombre)
                s0 = s['source_timerange']['start'] / 1e6; s1 = s0 + s['source_timerange']['duration'] / 1e6
                i0 = s['target_timerange']['start'] / 1e6
                if i0 < c0 or i0 >= c1: continue
                for w in trans[vi]['palabras']:
                    m = (w['s'] + w['e']) / 2
                    if s0 <= m <= s1:
                        base = t0 + i0 - c0 - s0
                        res.setdefault((ci, ti), []).append({'w': w['w'], 'ts': round(base + max(w['s'], s0), 3),
                            'te': round(base + min(w['e'], s1), 3), 'frase': frase_de.get((vi, w['s']), '?'),
                            'fin_clip': round(base + s1, 3), 'vi': vi, 'src': w['s']})
    for k in res: res[k].sort(key=lambda w: w['ts'])
    return res

if __name__ == '__main__':
    for k, ws in palabras().items():
        print(k, len(ws), p.tc(ws[0]['ts']), p.tc(ws[-1]['te']))
        if k[1] != 0: print('   ', ' '.join(w['w'] for w in ws))
