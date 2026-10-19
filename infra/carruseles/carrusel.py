#!/usr/bin/env python3
"""carrusel.py — la fábrica de carruseles: de una pieza JSON a PNG (1080×1350) + PDF.

    python3 infra/carruseles/carrusel.py --json pieza.json [--out DIR] [--motor auto|playwright|chrome]
                                         [--navegador RUTA] [--solo-validar] [--estricto] [--html]

Dos estilos (campo `estilo` del JSON):
  - "rm"       → carruseles de la cuenta de RM Agency (plantilla de memoria/clientes/rm-agency/
                 carruseles/_fuente, ahora con las diapositivas como datos).
  - "personal" → carruseles de fotos de la cuenta personal de Gerard (portada con foto + gancho,
                 texto / foto alternos, cierre con pregunta y «Capítol N, aviat»).

Salida en --out (por defecto, una carpeta junto al JSON con su `id`):
  <prefijo>-01.png … <prefijo>-NN.png · <id>.pdf (mismas páginas, para LinkedIn) · _vista.png (si hay Pillow)

Esquema completo y catálogo de dibujos: infra/carruseles/README.md.
Solo renderiza: no sube nada a Metricool ni a Notion (eso es de programar.py y de Gerard).

Navegador: hace falta un Chrome/Chromium. Por orden: --navegador, $CARRUSEL_CHROME, el Chromium de
Playwright (si está instalado el paquete `playwright` de Python) y, si no, el Chrome del sistema
(/Applications/Google Chrome.app en el Mac). Con --motor chrome no hace falta ningún paquete Python.
"""
import argparse
import base64
import html as _html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from dibujos import ARR, cta, dibujar, t  # noqa: E402

HUB = AQUI.parent.parent
PLANTILLA = AQUI / "plantilla"
FUENTES_RM = HUB / "infra" / "analisis" / "marca"
W, H = 1080, 1350
MAX_RM = 10          # copy-brief: máximo 10 diapositivas
MAX_IG = 20          # tope de Instagram (estilo personal)

# ============================================================================ validación

PALABRAS_NOSOTROS = re.compile(r"\b(nosotros|nuestr[oa]s?|RM Agency)\b", re.I)
PRECIO = re.compile(r"\d\s*(€|euros?\b)|€\s*\d", re.I)


def _textos(pieza):
    """Todos los textos visibles de la pieza (para las comprobaciones de reglas)."""
    out = []

    def rec(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k not in ("tipo", "foto", "html", "color", "icono", "estado", "nombre"):
                    rec(v)
        elif isinstance(x, list):
            for v in x:
                rec(v)
    rec({k: v for k, v in pieza.items() if k not in ("cifras_verificadas", "id", "prefijo", "estilo")})
    return out


def n_diapositivas(pieza):
    if pieza.get("estilo", "rm") == "personal":
        return 1 + 2 * len(pieza.get("fotos", [])) + 1
    return 1 + len(pieza.get("diapositivas", [])) + 1


def validar(pieza, base=None):
    """Devuelve (errores, avisos). Errores = no se puede renderizar o rompe una regla dura del brief."""
    err, av = [], []
    estilo = pieza.get("estilo", "rm")
    if estilo not in ("rm", "personal"):
        return [f"estilo desconocido: {estilo!r} (rm | personal)"], []
    if not pieza.get("id"):
        err.append("falta `id` (nombre de la pieza, p. ej. 08-mi-carrusel)")
    if estilo == "personal" and pieza.get("variante", "revista") not in VARIANTES_PERSONAL:
        err.append(f"variante desconocida: {pieza.get('variante')!r} ({' | '.join(VARIANTES_PERSONAL)})")
    n = n_diapositivas(pieza)

    if estilo == "rm":
        from dibujos import TIPOS
        if n > MAX_RM:
            err.append(f"{n} diapositivas: el máximo de RM es {MAX_RM} (portada + {MAX_RM - 2} + cierre)")
        if n < 3:
            err.append("hace falta portada, al menos una diapositiva y cierre")
        por = pieza.get("portada") or {}
        if not por.get("titular"):
            err.append("portada sin `titular`")
        if PALABRAS_NOSOTROS.search(" ".join(str(por.get(k, "")) for k in ("titular", "rotulo", "cifra"))):
            av.append("la portada habla de «nosotros»: tiene que hablar del que lee (copy-brief, 14/10)")
        for i, d in enumerate(pieza.get("diapositivas", []), start=2):
            if not d.get("titular") and not d.get("solo_pregunta"):
                err.append(f"diapositiva {i}: falta `titular`")
            dib = d.get("dibujo")
            if dib and dib.get("tipo") not in TIPOS:
                err.append(f"diapositiva {i}: dibujo {dib.get('tipo')!r} no existe")
            if dib and dib.get("tipo") == "html":
                av.append(f"diapositiva {i}: dibujo `html` a mano (Coco no debería usarlo)")
            if d.get("solo_pregunta") and i == 2 and not por.get("pregunta"):
                err.append("diapositiva 2: `solo_pregunta` sin pregunta en la portada")
            if dib and dib.get("tipo") == "cta":
                av.append(f"diapositiva {i}: CTA antes del cierre (la venta va solo al final)")
        for i, d in enumerate([por] + pieza.get("diapositivas", []), start=1):
            if len(d.get("pregunta") or "") > 42:
                av.append(f"diapositiva {i}: pregunta larga ({len(d['pregunta'])} caracteres), sale en dos líneas")
        cie = pieza.get("cierre") or {}
        if not cie.get("titular"):
            err.append("cierre sin `titular`")
        if (cie.get("palabra") or "ESTRATEGIA").upper() != "ESTRATEGIA":
            av.append(f"CTA con palabra {cie.get('palabra')!r}: la vigente es «ESTRATEGIA»")
        textos = _textos(pieza)
        if any(PRECIO.search(x) for x in textos):
            err.append("aparece un precio (€): fuera de los carruseles de RM (copy-brief, 14/10)")
        # Cifras: si la pieza trae su lista de verificadas, cada número visible tiene que estar en ella.
        if "cifras_verificadas" in pieza:
            ok = {re.sub(r"\D", "", str(c)) for c in pieza["cifras_verificadas"]}
            for x in textos:
                for c in re.findall(r"\d[\d.,]*", x):
                    dig = re.sub(r"\D", "", c)
                    if len(dig) >= 2 and dig not in ok:
                        av.append(f"cifra «{c}» no está en `cifras_verificadas` ({x[:50]}…)")
    else:
        if n > MAX_IG:
            err.append(f"{n} diapositivas: Instagram admite {MAX_IG} como mucho")
        elif n > 10:
            av.append(f"{n} diapositivas: más de 10, ¿seguro?")
        por = pieza.get("portada") or {}
        fotos = [por.get("foto")] + [f.get("foto") for f in pieza.get("fotos", [])]
        if not por.get("gancho"):
            err.append("portada sin `gancho` (el texto sobre la foto)")
        for i, f in enumerate(pieza.get("fotos", []), start=1):
            if not f.get("texto"):
                err.append(f"foto {i}: falta `texto` (la diapositiva que la presenta)")
        for f in fotos:
            if not f:
                err.append("falta alguna `foto`")
            elif base is not None and not _ruta(f, base).exists():
                err.append(f"no encuentro la foto: {f}")
        if not (pieza.get("cierre") or {}).get("pregunta"):
            err.append("cierre sin `pregunta` (la pregunta a los fotógrafos)")
    return err, av


# ============================================================================ HTML

def _b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def _ruta(f, base):
    p = Path(os.path.expanduser(f))
    return p if p.is_absolute() else (base / p)


# Encaje: si el dibujo no cabe en su hueco (titular de 3 líneas, dibujo alto…), se encoge lo justo
# para no pisar el pie. Con los textos de los carruseles a mano no salta (escala 1).
ENCAJE_JS = """<script>
function encajar(){document.querySelectorAll('.vis').forEach(v=>{
  const cs=getComputedStyle(v), r=v.getBoundingClientRect();
  const aw=document.body.clientWidth-120;  // a lo ancho puede salirse de la columna (c6), no del lienzo
  const ah=r.height-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
  const m=v.firstElementChild; if(!m) return;
  const b=m.getBoundingClientRect(), k=Math.min(1, aw/b.width, ah/b.height);
  if(k<1) [...v.children].forEach(c=>{c.style.transform='scale('+k.toFixed(3)+')';c.style.transformOrigin='center'});
});window.__listo=true}
document.fonts.ready.then(()=>requestAnimationFrame(encajar));
</script>"""


def _doc(css, cuerpo, titulo="carrusel"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{_html.escape(titulo)}</title>'
            f'<style>html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}{css}</style></head>'
            f'<body>{cuerpo}{ENCAJE_JS}</body></html>')


def css_rm():
    fuentes = (f'@font-face{{font-family:"Glacial";src:url(data:font/otf;base64,{_b64(FUENTES_RM / "GlacialIndifference-Regular.otf")}) format("opentype");font-weight:400}}'
               f'@font-face{{font-family:"Glacial";src:url(data:font/otf;base64,{_b64(FUENTES_RM / "GlacialIndifference-Bold.otf")}) format("opentype");font-weight:700}}')
    return fuentes + (PLANTILLA / "rm.css").read_text()


def _pie(pregunta, regalo=False, final=None):
    g = '<span class="gift"><b>🎁</b> Al final, algo gratis que te va a ayudar.</span>' if regalo else ""
    if pregunta:
        return f'<div class="foot">{g}<span class="bridge">{t(pregunta)}<i>{ARR}</i></span></div>'
    return f'<div class="foot">{g}<span class="sw">{t(final or "desliza →")}</span></div>'


def slides_rm(p):
    """Lista de <section> (una por diapositiva), con el hilo de preguntas resuelto."""
    por = p["portada"]
    out = [f'<section class="sl cv">' + (f'<div class="lbl">{t(por["rotulo"])}</div>' if por.get("rotulo") else "")
           + (f'<div class="num">{t(por["cifra"])}</div>' if por.get("cifra") else "")
           + f'<h2>{t(por["titular"], "em")}</h2>'
           + (f'<p class="sm">{t(por["apoyo"])}</p>' if por.get("apoyo") else "")
           + _pie(por.get("pregunta"), por.get("regalo")) + "</section>"]
    previa = por.get("pregunta")
    cuerpo = list(p.get("diapositivas", []))
    cie = dict(p["cierre"])
    for i, d in enumerate(cuerpo + [cie]):
        ultima = i == len(cuerpo)
        if d.get("solo_pregunta"):
            cab = f"<h2>{t(previa)}</h2>"
        else:
            ey = (f'<div class="ey q">{t(previa)}</div>' if previa else
                  f'<div class="ey">{t(d["rotulo"])}</div>' if d.get("rotulo") else "")
            cab = f'{ey}<h2>{t(d["titular"])}</h2>'
        sub = f'<p class="sub">{t(d["apoyo"])}</p>' if d.get("apoyo") else ""
        if ultima:
            vis = cta({"etiqueta": d.get("etiqueta", "Comenta"), "palabra": d.get("palabra", "ESTRATEGIA"),
                       "despues": d.get("despues")})
            pie = _pie(None, final=d.get("pie", "te escribimos por mensaje"))
        else:
            vis = dibujar(d.get("dibujo"))
            pie = _pie(d.get("pregunta"), d.get("regalo"))
        out.append(f'<section class="sl{" last" if ultima else ""}">{cab}{sub}<div class="vis">{vis}</div>{pie}</section>')
        previa = d.get("pregunta")
    return [f'<div class="pano t2">{s}</div>' for s in out]


VARIANTES_PERSONAL = ("revista", "diari", "llibreta", "impacte", "fosc", "club", "retro", "cartel")
FUENTES_PERSONAL = [  # (familia, archivo, estilo, peso) — todas OFL, en plantilla/fuentes
    ("Instrument", "InstrumentSerif-Regular.ttf", "normal", 400),
    ("Instrument", "InstrumentSerif-Italic.ttf", "italic", 400),
    ("Mono", "DMMono-Regular.ttf", "normal", 400),
    ("Brico", "BricolageGrotesque-Regular.ttf", "normal", 400),
    ("Brico", "BricolageGrotesque-Bold.ttf", "normal", 700),
    ("Mano", "NothingYouCouldDo-Regular.ttf", "normal", 400),
    ("Shoulders", "BigShoulders-Bold.ttf", "normal", 700),
    ("Grot", "WorkSans-Bold.ttf", "normal", 700),
    ("Young", "YoungSerif-Regular.ttf", "normal", 400),
    ("Gloock", "Gloock-Regular.ttf", "normal", 400),
    ("Tektur", "Tektur-Medium.ttf", "normal", 500),
]


def css_personal(variante="revista"):
    f = PLANTILLA / "fuentes"
    fuentes = "".join(f'@font-face{{font-family:"{fam}";src:url(data:font/ttf;base64,{_b64(f / arch)}) format("truetype");'
                      f'font-style:{est};font-weight:{peso}}}' for fam, arch, est, peso in FUENTES_PERSONAL)
    fuentes += (f'@font-face{{font-family:"Glacial";src:url(data:font/otf;base64,{_b64(FUENTES_RM / "GlacialIndifference-Regular.otf")}) format("opentype");font-weight:400}}')
    rocket = f / "propias" / "RocketBrush.otf"  # fuente de títulos de Gerard (licencia suya, fuera del repo)
    if rocket.exists():
        fuentes += f'@font-face{{font-family:"Titol";src:url(data:font/otf;base64,{_b64(rocket)}) format("opentype")}}'
    # Más fuentes de Gerard (licencia suya, fuera del repo): Architype R. para títulos, Lazydog a mano
    for fam, prefijo in (("Cartel", "architype"), ("Lazy", "lazy")):
        arch = next((a for a in sorted((f / "propias").glob("*")) if a.suffix.lower() in (".otf", ".ttf")
                     and a.stem.lower().replace(" ", "").startswith(prefijo)), None)
        if arch:
            fmt = "opentype" if arch.suffix.lower() == ".otf" else "truetype"
            fuentes += f'@font-face{{font-family:"{fam}";src:url(data:font/{arch.suffix[1:].lower()};base64,{_b64(arch)}) format("{fmt}")}}'
    css = fuentes + (PLANTILLA / "personal.css").read_text()
    extra = PLANTILLA / f"personal-{variante}.css"
    return css + (extra.read_text() if extra.exists() else "")


def slides_personal(p, base):
    def img(f, cls=""):
        uri = _ruta(f, base).resolve().as_uri()
        return f'<img class="{cls}" src="{_html.escape(uri)}">'

    v = f'v-{p.get("variante", "revista")}'
    cap = p.get("capitulo")
    serie = p.get("serie", "")
    etiqueta = " · ".join(x for x in [serie, f"Capítol {cap}" if cap else ""] if x)
    dia = p.get("dia") or (f"Dia {cap:02d}" if isinstance(cap, int) else "")
    firma = f'<div class="firma">{_html.escape(p.get("firma", "Gerard Ruiz"))}</div>'
    lbl = lambda extra="": (f'<div class="lbl {extra}">{_html.escape(etiqueta)}</div>' if etiqueta else "") + firma
    por = p["portada"]
    out = [f'<section class="ps {v} foto portada">{img(por["foto"])}<div class="velo"></div>'
           + lbl("clar")
           + (f'<div class="dia">{_html.escape(dia)}</div>' if dia else "")
           + f'<h1>{t(por["gancho"], "em")}</h1>'
           + (f'<p class="sub">{t(por["apoyo"], "em")}</p>' if por.get("apoyo") else "")
           + '<div class="seg clar">→</div></section>']
    fotos = p.get("fotos", [])
    for i, f in enumerate(fotos, 1):
        num = f'<div class="num">{i:02d}<span>/{len(fotos):02d}</span></div>'
        nota = f'<p class="nota">{t(f["nota"], "em")}</p>' if f.get("nota") else ""
        out.append(f'<section class="ps {v} text">{lbl()}{num}'
                   f'<p class="tx">{t(f["texto"], "em")}</p>{nota}<div class="seg">→</div></section>')
        encaje = f.get("encaje", "completa")
        peu = f'<p class="peu">{t(f["pie"], "em")}</p>' if f.get("pie") else ""
        dades = f'<div class="dades">{_html.escape(f["dades"])}</div>' if f.get("dades") else ""
        cls = "llena" if encaje == "llena" else "completa"
        out.append(f'<section class="ps {v} foto {cls}"><div class="marc">{img(f["foto"])}{dades}</div>{peu}{num}{firma}</section>')
    cie = p.get("cierre", {})
    sig = cie.get("capitulo", (cap + 1) if isinstance(cap, int) else None)
    aviat = cie.get("aviat") or (f"Capítol {sig}, aviat" if sig else "Aviat, més")
    out.append(f'<section class="ps {v} final">{lbl()}'
               f'<p class="q">{t(cie["pregunta"], "em")}</p>'
               + (f'<p class="sub">{t(cie["apoyo"], "em")}</p>' if cie.get("apoyo") else "")
               + f'<div class="aviat">{t(aviat, "em")}</div></section>')
    return out


# ============================================================================ render

MAC_CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")]


def chrome_sistema():
    for c in MAC_CHROME:
        if Path(c).exists():
            return c
    for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        if shutil.which(n):
            return shutil.which(n)
    pw = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or str(Path.home() / (
        "Library/Caches/ms-playwright" if platform.system() == "Darwin" else ".cache/ms-playwright"))
    for pat in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
                "chromium-*/chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium"):
        hits = sorted(Path(pw).glob(pat))
        if hits:
            return str(hits[-1])
    return None


def render_playwright(paginas, pngs, pdf_html, pdf, exe):
    from playwright.sync_api import sync_playwright
    args = ["--force-color-profile=srgb", "--allow-file-access-from-files"]
    with sync_playwright() as pw:
        try:
            nav = pw.chromium.launch(executable_path=exe, args=args)
        except Exception:
            if exe:
                raise
            alt = chrome_sistema()   # Mac sin `playwright install`: tira del Chrome instalado
            if not alt:
                raise
            nav = pw.chromium.launch(executable_path=alt, args=args)
        pg = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for src, dst in zip(paginas, pngs):
            pg.goto(src.as_uri(), wait_until="load")
            pg.evaluate("document.fonts.ready.then(() => Promise.all([...document.images].map(i => i.decode().catch(() => 0))))")
            pg.wait_for_function("window.__listo === true", timeout=10000)
            pg.screenshot(path=str(dst), clip={"x": 0, "y": 0, "width": W, "height": H})
        pg.goto(pdf_html.as_uri(), wait_until="load")
        pg.pdf(path=str(pdf), width=f"{W}px", height=f"{H}px", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        nav.close()


def render_chrome(paginas, pngs, pdf_html, pdf, exe):
    # Chrome headless resta la «barra» del navegador a la ventana (≈90 px): se pide una ventana más
    # alta y se recorta arriba a 1080×1350. El recorte necesita Pillow.
    try:
        from PIL import Image
    except ImportError:
        sys.exit("El motor chrome necesita Pillow para recortar: pip3 install pillow (o instala playwright).")
    base = [exe, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
            "--force-color-profile=srgb", "--allow-file-access-from-files", "--disable-gpu",
            "--virtual-time-budget=4000", f"--window-size={W},{H + 400}"]
    if platform.system() == "Linux" and os.geteuid() == 0:
        base.append("--no-sandbox")
    with tempfile.TemporaryDirectory() as perfil:
        base.append(f"--user-data-dir={perfil}")
        for src, dst in zip(paginas, pngs):
            subprocess.run(base + [f"--screenshot={dst}", src.as_uri()], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        for p in pngs:
            if not Path(p).exists():
                raise RuntimeError(f"Chrome no generó {p}")
            with Image.open(p) as im:
                im.load()
                recorte = im.crop((0, 0, W, H))
            recorte.save(p)
        subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", pdf_html.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    if not Path(pdf).exists():
        raise RuntimeError(f"Chrome no generó {pdf}")


def vista(pngs, dst, cols=5):
    """Hoja de contacto (como los _vista.png de los carruseles hechos a mano). Necesita Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return None
    w, h = 400, 500
    filas = (len(pngs) + cols - 1) // cols
    hoja = Image.new("RGB", (w * min(cols, len(pngs)), h * filas), "white")
    for i, p in enumerate(pngs):
        im = Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS)
        hoja.paste(im, ((i % cols) * w, (i // cols) * h))
    hoja.save(dst)
    return dst


def construir(pieza, base, out, motor="auto", navegador=None, guardar_html=False):
    estilo = pieza.get("estilo", "rm")
    if estilo == "personal":
        css, secciones = css_personal(pieza.get("variante", "revista")), slides_personal(pieza, base)
    else:
        css, secciones = css_rm(), slides_rm(pieza)
    out.mkdir(parents=True, exist_ok=True)
    prefijo = pieza.get("prefijo") or pieza["id"]
    pngs = [out / f"{prefijo}-{i:02d}.png" for i in range(1, len(secciones) + 1)]
    pdf = out / f"{pieza['id']}.pdf"

    tmp = Path(tempfile.mkdtemp(prefix="carrusel-"))
    try:
        paginas = []
        for i, s in enumerate(secciones, 1):
            f = tmp / f"{i:02d}.html"
            f.write_text(_doc(css, s, f"{pieza['id']} {i}"), encoding="utf-8")
            paginas.append(f)
        # El PDF lleva las mismas páginas que los PNG (las imágenes ya renderizadas: idéntico al carrusel).
        pdf_html = tmp / "pdf.html"
        imgs = "".join(f'<img src="{p.resolve().as_uri()}">' for p in pngs)
        pdf_html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W}px {H}px;margin:0}}'
                            f'html,body{{margin:0}}img{{display:block;width:{W}px;height:{H}px;break-after:page}}'
                            f'</style></head><body>{imgs}</body></html>', encoding="utf-8")

        exe = navegador or os.environ.get("CARRUSEL_CHROME") or None
        if motor == "auto":
            try:
                import playwright  # noqa: F401
                motor = "playwright"
            except ImportError:
                motor = "chrome"
        if motor == "playwright":
            # El PDF necesita los PNG ya hechos: se renderizan primero y el PDF después, en la misma sesión.
            render_playwright(paginas, pngs, pdf_html, pdf, exe)
        else:
            exe = exe or chrome_sistema()
            if not exe:
                sys.exit("No encuentro Chrome/Chromium. Pásalo con --navegador RUTA o $CARRUSEL_CHROME.")
            render_chrome(paginas, pngs, pdf_html, pdf, exe)
        if guardar_html:
            for f in paginas:
                shutil.copy(f, out / f"{prefijo}-{f.name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    v = vista(pngs, out / "_vista.png")
    return pngs, pdf, v, motor


def main():
    ap = argparse.ArgumentParser(description="Renderiza un carrusel (PNG 1080×1350 + PDF) desde una pieza JSON.")
    ap.add_argument("--json", required=True, help="pieza .json (esquema en infra/carruseles/README.md)")
    ap.add_argument("--out", help="carpeta de salida (por defecto: <carpeta del json>/<id>/)")
    ap.add_argument("--motor", choices=["auto", "playwright", "chrome"], default="auto",
                    help="auto = Playwright de Python si está instalado; si no, Chrome por línea de comandos")
    ap.add_argument("--navegador", help="ruta del ejecutable de Chrome/Chromium (o $CARRUSEL_CHROME)")
    ap.add_argument("--solo-validar", action="store_true", help="comprueba las reglas y no renderiza")
    ap.add_argument("--estricto", action="store_true", help="los avisos también paran")
    ap.add_argument("--html", action="store_true", help="guarda también el HTML de cada diapositiva")
    a = ap.parse_args()

    src = Path(a.json).resolve()
    pieza = json.loads(src.read_text(encoding="utf-8"))
    err, av = validar(pieza, src.parent)
    for x in av:
        print(f"⚠️  {x}")
    for x in err:
        print(f"❌ {x}")
    if err or (a.estricto and av):
        sys.exit(1)
    print(f"✓ {pieza['id']}: {n_diapositivas(pieza)} diapositivas, estilo {pieza.get('estilo', 'rm')}")
    if a.solo_validar:
        return
    out = Path(a.out).resolve() if a.out else src.parent / pieza["id"]
    pngs, pdf, v, motor = construir(pieza, src.parent, out, a.motor, a.navegador, a.html)
    print(f"✓ {len(pngs)} PNG + PDF en {out} (motor: {motor})")
    print(f"  {pdf.name}" + (f" · {v.name}" if v else ""))


if __name__ == "__main__":
    main()
