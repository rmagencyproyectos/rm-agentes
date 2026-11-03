"""Subtítulos DENTRO de cada clip combinado + recorte del negro final. CapCut cerrado."""
import sys, json, subprocess, shutil, glob, copy
sys.path.insert(0, '.')
import mapa, precapcut as p
from pathlib import Path
PROY = mapa.PROY; D = mapa.D
TMP = Path('tmpproy')
R = json.load(open('retrans/interno-medium.json'))
estilo = p.leer_json(p.AQUI / 'estilos' / 'gerard-personal.json'); e = estilo['subtitulos']
info = json.loads((PROY / 'draft_info.json').read_text())
drafts = {dr['id']: dr['draft'] for dr in info['materials']['drafts']}
orden = [next(r for r in s['extra_material_refs'] if r in drafts) for s in info['tracks'][0]['segments']]

def unir(ws):
    out = []
    for w in ws:
        if out and w['w'][:1] in "'-":
            out[-1]['w'] += w['w']; out[-1]['e'] = w['e']
        else:
            out.append(dict(w))
    return out

def cambiar(ws, viejo, nuevo):
    v = viejo.split(); n = nuevo.split()
    for i in range(len(ws) - len(v) + 1):
        if [x['w'] for x in ws[i:i + len(v)]] == v:
            s, e2 = ws[i]['s'], ws[i + len(v) - 1]['e']; paso = (e2 - s) / len(n)
            ws[i:i + len(v)] = [{'w': t, 's': round(s + k * paso, 3), 'e': round(s + (k + 1) * paso, 3), 'p': 1} for k, t in enumerate(n)]
            return True
    print('  NO ENCONTRADO:', viejo); return False

FIXES = [("I per al cantor", "I pel cantó"), ("els del cantor", "els del cantó"), ("d'un to que", "d'un toll que"),
         ("d'un fotogràfic.", "d'un fotògraf."), ("Del loal deu,", "De l'u al deu,"), ("Avui 6 esportiva", "Avui sessió esportiva"),
         ("Era u 400", "Era 1/400"), ("potser u 800.", "potser 1/800."), ("també és art.", "també és cert."),
         ("com un nenano.", "com un enano."), ("Ens ho empassarem.", "Ens ho vam passar bé."),
         ("Seguim per vingut.", "Seguim per a bingo."), ("Volveu dir un triple?", "M'acabo de tirar un triple..."),
         ("I diu-me,", "Digueu-me,")]
GANXOS = {466.667: "I per últim, la foto number one, la que més m'agrada és...",
          385.7: "Aquí ja em vaig ficar una mica més creatiu, creatiu potser sense criteri, però creatiu.",
          114.233: "Ah no, ja té prou zoom, jeje.",
          801.7: "Si veieu tolls, utilitzeu-los.", 367.667: "Com sempre, portem un episodi, però és igual."}

def frases(ws):
    f, res = 0, []
    for w in ws:
        res.append({'w': w['w'], 'ts': w['s'], 'te': w['e'], 'frase': f, 'fin_clip': 1e9})
        if w['w'][-1] in '.?!': f += 1
    return res

def pista_texto(did):
    """{nombre: palabras} en tiempo interno del clip combinado."""
    dr = drafts[did]; vids = {m['id']: m['path'] for m in dr['materials']['videos']}
    trans = {Path(t['video']).name: t for t in mapa.trans}
    out = {}
    for ti, t in enumerate(dr['tracks']):
        segs = [s for s in t['segments'] if str(vids.get(s['material_id'], '')).lower().endswith('.mp4')]
        if not segs: continue
        if ti == 0:
            ws = unir(R[f'{did},0'])
            for a, b in FIXES:
                if any(w['w'] == a.split()[0] for w in ws): cambiar(ws, a, b)
            out['Subtitulos'] = frases(ws)
            continue
        for k, s in enumerate(segs):   # cada gancho: el texto de Gerard repartido sobre su voz
            src = s['source_timerange']['start'] / 1e6; du = s['source_timerange']['duration'] / 1e6
            i0 = s['target_timerange']['start'] / 1e6
            txt = next(v for kk, v in GANXOS.items() if abs(kk - src) < 0.1)
            nombre = Path(vids[s['material_id']]).name
            voz = [w for w in trans[nombre]['palabras'] if src <= (w['s'] + w['e']) / 2 <= src + du]
            a = max(0.02, voz[0]['s'] - src) if voz else 0.1; b = min(du - 0.02, voz[-1]['e'] - src) if voz else du - 0.1
            n = txt.split(); paso = (b - a) / len(n)
            ws = [{'w': x, 's': round(i0 + a + j * paso, 3), 'e': round(i0 + a + (j + 1) * paso, 3)} for j, x in enumerate(n)]
            out[f"Subtitulos ganxo {ti}" + (f"-{k + 1}" if len(segs) > 1 else '')] = frases(ws)
    return out

nuevos = {}
for did in orden:
    pistas = pista_texto(did)
    tmp = TMP / did
    shutil.rmtree(tmp, ignore_errors=True); shutil.copytree(PROY, tmp, ignore=shutil.ignore_patterns('.locked', 'subdraft', 'Timelines'))
    for f in ('draft_content.json', 'template-2.tmp'):
        if (tmp / f).exists(): (tmp / f).unlink()
    tinfo = tmp / 'draft_info.json'
    td0 = json.loads(tinfo.read_text())  # el temporal sin ningún texto: caption añade a una pista con el mismo nombre
    td0['tracks'] = [t for t in td0['tracks'] if t['type'] != 'text']; td0['materials']['texts'] = []
    td0['duration'] = max(td0['duration'], 600_000_000)
    tinfo.write_text(json.dumps(td0, ensure_ascii=False))
    for nombre, ws in pistas.items():
        cues, _ = p.construir_cues(ws, e, {'correcciones': {}})
        pal, lin = [], []
        for c in cues:
            t = c['texto'].split(); paso = (c['fin'] - c['ini']) / len(t)
            pal += [{'word': w, 'start': round(c['ini'] + j * paso, 3), 'end': round(c['ini'] + (j + 1) * paso, 3)} for j, w in enumerate(t)]
            lin.append(c['texto'])
        p.escribir_json(tmp / 'pal.json', pal); (tmp / 'guion.txt').write_text('\n'.join(lin) + '\n', encoding='utf-8')
        p.preset_de(e, tmp / 'preset.json', e.get('x', 0), e.get('y', 0))
        r = subprocess.run([p.capcut_bin(), 'caption', str(tinfo), '--words', str(tmp / 'pal.json'), '--script', str(tmp / 'guion.txt'),
                            '--track-name', nombre, '--preset', str(tmp / 'preset.json')], capture_output=True, text=True)
        print(did[:4], nombre, len(cues), 'ok' if r.returncode == 0 else (r.stdout + r.stderr)[-400:])
        if r.returncode: sys.exit(1)
    for nombre in pistas:
        p.colocar_pista(tmp, nombre, e.get('x', 0), e.get('y', 0)); p.a_formato_subtitulo(tmp, nombre, 'ca-ES')
    p.fijar_fuentes(tmp, estilo)
    td = json.loads(tinfo.read_text())
    tr = [t for t in td['tracks'] if t['type'] == 'text' and t.get('name') in pistas]
    ids = {s['material_id'] for t in tr for s in t['segments']}
    nuevos[did] = (tr, [m for m in td['materials']['texts'] if m['id'] in ids])
json.dump({k: v for k, v in nuevos.items()}, open('nuevos.json', 'w'), ensure_ascii=False)
print('listo')
