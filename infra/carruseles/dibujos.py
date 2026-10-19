"""Dibujos (maquetas) de los carruseles RM, como datos.

Cada diapositiva lleva un `dibujo` = {"tipo": "<nombre>", ...campos}. Este módulo convierte ese
diccionario en el HTML de la plantilla (las clases CSS viven en plantilla/rm.css, extraídas de la
plantilla a mano de los 7 primeros carruseles). El catálogo con los campos de cada tipo está en
infra/carruseles/README.md — si añades un tipo aquí, añádelo allí.

Todo texto que llega del JSON pasa por `t()` (escapa HTML y respeta *marcado*).
"""
import html
import re

# --- iconos (copiados de la plantilla) ---
ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
EYE = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" fill="#fff"><path d="M7 4l13 8-13 8z"/></svg>'
TICK = '<svg viewBox="0 0 24 24" fill="none" stroke="#ff2041" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
WARN = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"><path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/></svg>'
LUPA = '<svg viewBox="0 0 24 24" fill="none" stroke="#948e9c" stroke-width="2.4"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>'
YT = '<svg viewBox="0 0 64 46"><rect width="64" height="46" rx="12" fill="#ff0033"/><path d="M26 14l16 9-16 9z" fill="#fff"/></svg>'
PIN = '<svg width="56" height="72" viewBox="0 0 40 52"><path d="M20 0C9 0 0 9 0 20c0 15 20 32 20 32s20-17 20-32C40 9 31 0 20 0z" fill="{c}"/><circle cx="20" cy="19" r="7" fill="#fff"/></svg>'
COLGAR = '<svg viewBox="0 0 24 24" fill="#fff"><path d="M3 15c5-4 13-4 18 0l-2 3-4-1v-3c-2-.6-4-.6-6 0v3l-4 1z"/></svg>'
DESCOLGAR = '<svg viewBox="0 0 24 24" fill="#fff"><path d="M6 3l3 4-2 2c1 3 4 6 7 7l2-2 4 3-2 3C10 20 4 14 3 5z"/></svg>'

ON = ' class="on"'
COLORES = {"gris": "#d8d4de", "medio": "#948e9c", "oscuro": "var(--ink)", "rojo": "var(--red)"}
BAR = '<div class="bar"><b></b><b></b><b></b><span>{}</span></div>'


def t(s, marca="hl"):
    """Texto seguro: escapa HTML, *así* → palabra marcada, salto de línea → <br>."""
    s = html.escape(str(s or ""), quote=False)
    if marca == "em":
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    else:
        s = re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', s)
    return s.replace("\n", "<br>")


def _num(cifra):
    """'89.679' → 89679 · '2,4 M' → 2400000 · '38 k' → 38000. None si no hay número."""
    m = re.search(r"(\d[\d.]*(?:,\d+)?)\s*([kKmM])?", str(cifra))
    if not m:
        return None
    n = float(m.group(1).replace(".", "").replace(",", "."))
    return n * {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1)


# --------------------------------------------------------------------------- tipos

def barras(d):
    bs = d["barras"]
    nums = [_num(b.get("cifra")) or 0 for b in bs]
    mx = max(nums) or 1
    ancho = d.get("ancho") or (700 if len(bs) <= 2 else None)
    out = []
    for i, (b, n) in enumerate(zip(bs, nums)):
        alto = b.get("alto")
        if alto is None:
            alto = max(2, round(100 * n / mx))
        color = b.get("color") or ("rojo" if n == mx else "gris")
        out.append(f'<div class="b" style="height:{alto}%;background:{COLORES.get(color, color)}">'
                   f'<span>{t(b.get("cifra"))}</span><em>{t(b.get("etiqueta"))}</em></div>')
    st = f' style="width:{ancho}px"' if ancho else ""
    return f'<div class="chart"{st}>{"".join(out)}</div>'


def pantallas(d):
    out = []
    for p in d["pantallas"]:
        ic = EYE if p.get("icono") == "ojo" else PLAY
        out.append(f'<div class="scr{" big" if p.get("destacada") else ""}"><span class="net">{t(p.get("red"))}</span>'
                   f'<div class="cnt">{ic}{t(p.get("cifra"))}</div></div>')
    return f'<div class="duo">{"".join(out)}</div>'


def lista(d):
    return '<div class="card checklist">' + "".join(f"<div><i></i>{t(x)}</div>" for x in d["items"]) + "</div>"


def ranking(d):
    filas = "".join(f'<div><em>{i + 1}</em><span>{t(x["texto"])}</span><b>{t(x.get("cifra"))}</b></div>'
                    for i, x in enumerate(d["items"]))
    pie = f'<p>{t(d["pie"])}</p>' if d.get("pie") else ""
    return f'<div class="card toplist">{filas}{pie}</div>'


def cadena(d):
    pasos = d["pasos"]
    on = d.get("destacado", len(pasos) - 1)
    spans = [f'<span{ON if i == on else ""}>{t(p)}</span>' for i, p in enumerate(pasos)]
    return f'<div class="chain{" sm" if d.get("compacta") else ""}">{TICK.join(spans)}</div>'


def notas(d):
    lineas = []
    for x in d.get("lineas", []):
        if isinstance(x, dict):
            txt = t(x.get("texto"))
            if x.get("tachado"):
                txt = f'<span class="strk">{txt}</span>'
            st = "color:var(--ink)" + (";font-weight:700" if x.get("negrita") else "")
            lineas.append(f'<div class="ln" style="{st}">{txt}</div>')
        else:
            lineas.append(f'<div class="ln" style="color:var(--ink)">{t(x)}</div>')
    if d.get("cursor", not lineas):
        lineas.insert(0, '<div class="ln"><span class="caret"></span></div>')
    lineas += ['<div class="ln"></div>'] * int(d.get("vacias", 3 if len(lineas) <= 1 else 1))
    reloj = f'<div class="clock">{t(d["reloj"])}</div>' if d.get("reloj") else ""
    st = ' style="position:relative;overflow:visible"' if reloj else ""
    return (f'<div class="card notes"{st}>{BAR.format(t(d.get("barra", "Notas")))}'
            f'<h4>{t(d.get("titulo", ""))}</h4>{"".join(lineas)}{reloj}</div>')


def buscador(d):
    q = f'<div class="q">{LUPA}{t(d["consulta"])}</div>' if d.get("consulta") else BAR.format(t(d.get("barra", "Instagram")))
    sello = f'<span class="badge">{t(d["sello"])}</span>' if d.get("sello") else ""
    return (f'<div class="card search">{q}<div class="res"><i></i><div><b>{t(d.get("nombre"))}</b>'
            f'<span>{t(d.get("detalle"))}</span></div>{sello}</div></div>')


def aviso(d):
    blur = "".join(f'<div class="blur" style="width:{w}%"></div>' for w in [90, 70, 80][:int(d.get("lineas_borrosas", 2))])
    return (f'<div class="card alert"><div class="hd">{WARN}{t(d.get("titulo", "Cuidado con esto"))}</div>'
            f'<div class="bd">{t(d.get("texto", ""))}{blur}</div></div>')


def tachados(d):
    return '<div class="btns2">' + "".join(f"<span>{t(b)}</span>" for b in d["botones"]) + "</div>"


def compartir(d):
    cs = []
    for c in d["contactos"]:
        c = c if isinstance(c, dict) else {"nombre": c}
        ini = c.get("inicial") or c["nombre"][:1].upper()
        cs.append(f'<div><i>{t(ini)}</i>{t(c["nombre"])}</div>')
    enviado = f'<div class="sent">{t(d["enviado"])}</div>' if d.get("enviado", "✓ Enviado") else ""
    return f'<div class="card share"><h4>{t(d.get("titulo", "Enviar a…"))}</h4><div class="row">{"".join(cs)}</div>{enviado}</div>'


def cta(d):
    despues = f'<div class="then">{t(d["despues"])}</div>' if d.get("despues") else ""
    return (f'<div class="kw"><div class="lbl">{t(d.get("etiqueta", "Comenta"))}</div>'
            f'<div class="word">{t(d.get("palabra", "ESTRATEGIA"))}</div>{despues}</div>')


def chat(d):
    out = []
    for m in d["mensajes"]:
        quien = m.get("quien", "")
        ini = m.get("inicial") or quien[:1].upper()
        col = m.get("color")
        st = f' style="background:{COLORES.get(col, col)}"' if col else ""
        small = f"<small>{t(quien)}</small>" if quien else ""
        out.append(f'<div class="msg{" r" if m.get("lado") == "der" else ""}"><div class="av"{st}>{t(ini)}</div>'
                   f'<div class="tx">{small}{t(m["texto"])}</div></div>')
    return f'<div class="chats">{"".join(out)}</div>'


def whatsapp(d):
    ms = "".join(f'<div class="wam">{t(m["texto"])}<small>{t(m.get("hora", ""))}</small></div>' for m in d["mensajes"])
    return (f'<div class="card wa"><div class="wah"><i></i><div><b>{t(d.get("contacto", "Cliente"))}</b>'
            f'<span>{t(d.get("estado", "escribiendo…"))}</span></div></div><div class="wab">{ms}</div></div>')


def movil(d):
    ns = []
    for n in d.get("notificaciones", []):
        st = ' style="background:#5c5563"' if n.get("gris") else ""
        ns.append(f'<div class="notif"><div class="ic"{st}></div><div><b>{t(n.get("app", "Instagram"))}</b>'
                  f'<span>{t(n["texto"])}</span></div></div>')
    return (f'<div class="phone"><div class="time">{t(d.get("hora", "09:41"))}</div>'
            f'<div class="date">{t(d.get("fecha", ""))}</div>{"".join(ns)}</div>')


def comentarios(d):
    out = []
    for c in d["comentarios"]:
        cls = " reply" if c.get("respuesta") else ""
        small = f'<small>{t(c["quien"])}</small>' if c.get("quien") else ""
        out.append(f'<div class="cm{cls}"><div class="av"></div><div class="tx">{small}{t(c["texto"])}</div></div>')
    return f'<div class="comments">{"".join(out)}</div>'


def bandeja(d):
    filas = "".join(f'<div class="row"><i></i><span>{t(m)}</span><small>{t(d.get("hora", "ahora"))}</small><b class="dot"></b></div>'
                    for m in d["mensajes"])
    badge = f'<span class="badge2">{t(d["contador"])}</span>' if d.get("contador") else ""
    return (f'<div class="card inbox" style="position:relative;overflow:visible">{BAR.format(t(d.get("barra", "Mensajes")))}'
            f'{filas}{badge}</div>')


def etiquetas(d):
    on = d.get("destacada")
    return '<div class="ideas">' + "".join(
        f'<span{ON if i == on else ""}>{t(x)}</span>' for i, x in enumerate(d["items"])) + "</div>"


def pasos(d):
    out = []
    for p in d["pasos"]:
        cls = {"on": ' class="on"', "apagado": ' class="fade"'}.get(p.get("estado"), "")
        out.append(f'<div{cls}><em>{t(p.get("etiqueta", ""))}</em>{t(p["texto"])}</div>')
    return f'<div class="steps">{"".join(out)}</div>'


def episodios(d):
    out = []
    for e in d["items"]:
        e = e if isinstance(e, dict) else {"texto": e}
        if e["texto"] in ("···", "...", "…"):
            out.append('<div class="dots">···</div>')
        else:
            out.append(f'<div{ON if e.get("on") else ""}>{t(e["texto"])}</div>')
    return f'<div class="eps">{"".join(out)}</div>'


def programacion(d):
    filas = []
    for f in d["filas"]:
        nuevo = f'<span class="new">{t(f["nuevo"])}</span>' if f.get("nuevo") else ""
        filas.append(f'<div class="row{" on" if f.get("on") else ""}"><b>{t(f["hora"])}</b>{t(f["texto"])}{nuevo}</div>')
    return f'<div class="card guide">{BAR.format(t(d.get("barra", "Programación")))}{"".join(filas)}</div>'


def ruta(d):
    a, b = d["desde"], d["hasta"]
    return ('<div class="route"><svg viewBox="0 0 860 420"><path d="M120 300 C 300 120, 520 380, 740 170" fill="none" '
            'stroke="#15121a" stroke-width="6" stroke-dasharray="2 18" stroke-linecap="round"/></svg>'
            f'<div class="pin" style="left:120px;top:300px"><span>{t(a)}</span>{PIN.format(c="#ff2041")}</div>'
            f'<div class="pin" style="left:740px;top:170px"><span>{t(b)}</span>{PIN.format(c="#15121a")}</div>'
            + (f'<div class="km">{t(d["distancia"])}</div>' if d.get("distancia") else "") + "</div>")


def ab(d):
    return ('<div class="ab"><svg viewBox="0 0 860 360"><path d="M110 240 C 300 60, 560 360, 750 140" fill="none" '
            'stroke="#15121a" stroke-width="6" stroke-dasharray="2 22" stroke-linecap="round"/></svg>'
            '<div class="pt" style="left:110px;top:240px;background:var(--ink)">A</div>'
            '<div class="pt" style="left:750px;top:140px;background:var(--red)">B</div>'
            f'<div class="lab" style="left:110px;top:315px">{t(d.get("desde", ""))}</div>'
            f'<div class="lab" style="left:750px;top:215px">{t(d.get("hasta", ""))}</div></div>')


def youtube(d):
    reqs = "".join(f'<div class="req"><div class="l"><span>{t(r["texto"])}</span><b>{t(r.get("valor", ""))}</b></div>'
                   f'<div class="t"><i style="width:{int(r.get("pct", 100))}%"></i></div></div>' for r in d["requisitos"])
    ok = f'<span class="ok">{t(d["estado"])}</span>' if d.get("estado") else ""
    return f'<div class="card yt"><div class="hd">{YT}{t(d.get("titulo", "Programa de Partners"))}{ok}</div>{reqs}</div>'


def llamada(d):
    return (f'<div class="call"><div class="av"></div><b>{t(d.get("nombre", "Cliente"))}</b>'
            f'<span>{t(d.get("estado", "llamada entrante…"))}</span><div class="btns">'
            f'<i style="background:#ff3b30">{COLGAR}</i><i style="background:#34c759">{DESCOLGAR}</i></div></div>')


def reels(d):
    return '<div class="reels">' + "".join(
        f'<div class="reel{" hot" if r.get("destacado") else ""}">{t(r.get("cifra", ""))}</div>'
        for r in (x if isinstance(x, dict) else {"cifra": x} for x in d["reels"])) + "</div>"


# Ilustraciones fijas con preguntas flotando alrededor (c4: la cómoda de la abuela).
ILUS = {
    "comoda": ('<svg viewBox="0 0 520 520"><rect x="70" y="90" width="380" height="330" rx="18" fill="#b9814f"/>'
               '<rect x="50" y="70" width="420" height="34" rx="10" fill="#8a5a36"/>'
               + "".join(f'<rect x="100" y="{130 + i * 95}" width="320" height="76" rx="10" fill="#c99260" stroke="#8a5a36" stroke-width="4"/>'
                         f'<circle cx="210" cy="{168 + i * 95}" r="9" fill="#5a3a22"/><circle cx="310" cy="{168 + i * 95}" r="9" fill="#5a3a22"/>'
                         for i in range(3))
               + '<path d="M95 420 q-10 50 -30 70 M425 420 q10 50 30 70" stroke="#8a5a36" stroke-width="16" fill="none" stroke-linecap="round"/></svg>'),
    "casa": ('<svg viewBox="0 0 100 80" fill="none" stroke="#15121a" stroke-width="3"><path d="M10 40 L50 8 L90 40"/>'
             '<path d="M20 34 V76 H80 V34"/><rect x="42" y="52" width="16" height="24"/><rect x="28" y="44" width="10" height="10"/>'
             '<rect x="62" y="44" width="10" height="10"/></svg>'),
}
POS_PREGUNTAS = ["left:-160px;top:40px", "right:-170px;top:180px", "left:-130px;top:360px", "right:-150px;top:440px"]


def ilustracion(d):
    svg = ILUS[d["nombre"]]
    tags = "".join(f'<div class="tagq" style="{POS_PREGUNTAS[i % 4]}">{t(q)}</div>' for i, q in enumerate(d.get("preguntas", [])))
    return f'<div class="dresser">{svg}{tags}</div>'


def html_crudo(d):
    """Escape: HTML tal cual (solo para piezas hechas a mano; Coco NO lo usa)."""
    return d["html"]


TIPOS = {
    "barras": barras, "pantallas": pantallas, "lista": lista, "ranking": ranking, "cadena": cadena,
    "notas": notas, "buscador": buscador, "aviso": aviso, "tachados": tachados, "compartir": compartir,
    "cta": cta, "chat": chat, "whatsapp": whatsapp, "movil": movil, "comentarios": comentarios,
    "bandeja": bandeja, "etiquetas": etiquetas, "pasos": pasos, "episodios": episodios,
    "programacion": programacion, "ruta": ruta, "ab": ab, "youtube": youtube, "llamada": llamada,
    "reels": reels, "ilustracion": ilustracion, "html": html_crudo,
}

# Reacciones/notas flotando encima del dibujo (posiciones fijas, en orden).
POS_REACCION = ["right:70px;top:120px", "left:40px;top:330px", "left:60px;top:90px", "right:50px;bottom:200px"]


def dibujar(d):
    if not d:
        return ""
    tipo = d.get("tipo")
    if tipo not in TIPOS:
        raise ValueError(f"dibujo de tipo desconocido: {tipo!r} (tipos: {', '.join(sorted(TIPOS))})")
    out = TIPOS[tipo](d)
    for i, r in enumerate(d.get("reacciones", [])):
        out += f'<div class="react" style="{POS_REACCION[i % 4]}">{t(r)}</div>'
    if d.get("nota"):
        out += f'<div class="note" style="right:40px;bottom:190px;rotate:-4deg">{t(d["nota"])}</div>'
    return out
