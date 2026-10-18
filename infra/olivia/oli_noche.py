#!/usr/bin/env python3
"""Oli sola, de madrugada: la tanda del mes para cada cliente que está en su semana 📊 Analizar.

Decisión de Gerard (22/09/2026): Oli deja de depender de que alguien abra su sesión a mano
(así se perdió la tanda de Jesús Mora de septiembre). Corre **la noche del martes al miércoles**
de la semana de Analizar de cada cliente, deja las ideas en la Bandeja como `Autor = Oli` y
avisa por **WhatsApp y correo**. Gerard solo aprueba o descarta en Notion (vista
🤖 Propuestas de Oli). El sábado, si queda algo sin revisar, se le recuerda.

Por qué martes→miércoles: el vídeo del domingo ya tiene ~58 h, y la semana de guiones empieza
el lunes siguiente, así que quedan de miércoles a domingo para revisar. El termómetro solo
cuenta piezas con 14+ días, así que un vídeo recién subido nunca contamina el análisis.

Lo que Oli pierde al no conversar lo recupera con los **descartes**: lee lo que Gerard ha
marcado `Descartada` en la Bandeja y el motivo que escribió en Notas, y no lo repite.

Idempotente: una tanda por cliente y mes (marca `oli_auto` en `hipotesis.json`). Algunos meses
tienen dos miércoles en la misma semana de Analizar; el segundo no hace nada.

Uso:
  oli_noche.py [--cliente <slug>] [--dry-run] [--forzar]   genera las tandas que toquen hoy
  oli_noche.py --recordatorio                              sábado: avisa de lo que sigue sin revisar
  oli_noche.py --cliente <slug> --prueba --forzar          llama a Oli e imprime; no escribe ni avisa
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
sys.path.insert(0, os.path.join(HUB, "infra/estado"))
import ciclo  # noqa: E402
import etiquetas_idea as ei  # noqa: E402
import notion_api as na  # noqa: E402

MODELO = "claude-sonnet-5"
PRESUPUESTO_USD = "1.50"      # una tanda de 8 piezas al mes por cliente
NOTIFY = os.path.join(HUB, "infra/notifier/notify.sh")
INBOX = os.path.join(HUB, "INBOX-GERARD.md")
PLANTILLAS = os.path.join(HUB, "agentes/guiones/plantillas")
PY = "/usr/bin/python3"
VISTA_OLI = ("https://www.notion.so/1a033425f19546edbccdb29b2e6163bb"
             "?v=3e3496ca6d518180bf98000c74142ac8")


def leer(*p, limite=None):
    try:
        with open(os.path.join(*p), encoding="utf-8") as f:
            t = f.read()
    except OSError:
        return ""
    # Del registro de aprendizajes interesa lo último: se recorta por el principio.
    return t[-limite:] if limite and len(t) > limite else t


def correr(*args):
    """Salida de un script del hub (termómetro, etc.), o cadena vacía si falla."""
    try:
        r = subprocess.run([PY, *args], capture_output=True, text=True, timeout=120, cwd=HUB)
        return r.stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def plantillas():
    return sorted(f[:-3] for f in os.listdir(PLANTILLAS)
                  if f.endswith(".md") and not f.startswith(("_", "README")))


def ruta_tanda(slug, mes):
    return os.path.join(HUB, "ciclos", mes, slug, "hipotesis.json")


def cargar(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def ya_hecha(slug, mes):
    d = cargar(ruta_tanda(slug, mes))
    return bool(d and d.get("oli_auto"))


def restricciones_previas(slug):
    """Las restricciones de la tanda más reciente del cliente: se heredan."""
    import glob
    for ruta in sorted(glob.glob(os.path.join(HUB, "ciclos", "*", slug, "hipotesis.json")),
                       reverse=True):
        d = cargar(ruta)
        if d and d.get("restricciones"):
            return d["restricciones"]
    return []


def bandeja_del_cliente(slug, tok, cfg):
    """(descartadas con motivo, títulos ya en marcha) de la Bandeja + la base del cliente."""
    descartadas, en_marcha = [], []
    filtro = {"property": "Cliente", "select": {"equals": slug}}
    for f in na.query(cfg["bandeja"]["database_id"], tok, filtro):
        p = f["properties"]
        idea = (na.plain(p.get("Idea")) or "").strip()
        estado = na.plain(p.get("Estado"))
        if estado == "Descartada":
            descartadas.append(f"- {idea[:120]} → motivo: {(na.plain(p.get('Notas')) or 'sin motivo escrito')[:200]}")
        elif estado in ("Nueva", "Aprobada") and idea:
            en_marcha.append(f"- {idea[:120]}")
    cli = cfg["clientes"].get(slug)
    if cli:
        filtro = {"property": "Producción", "select": {"equals": "Pendiente de grabar"}}
        en_marcha += [f"- {(na.plain(f['properties'].get('Idea')) or '')[:120]}"
                      for f in na.query(cli["database_id"], tok, filtro)]
    return descartadas[-40:], en_marcha[:60]


def construir_prompt(slug, label, mes, tok, cfg):
    descartadas, en_marcha = bandeja_del_cliente(slug, tok, cfg)
    opciones = ei.opciones(cfg["clientes"][slug]["database_id"], tok)
    base_cli = os.path.join(HUB, "memoria/clientes", slug)
    bloques = [
        ("TU FICHA (Oli, estratega) — respeta el §2, contrato de transparencia",
         leer(HUB, "agentes/estratega.md")),
        ("LA TANDA ANTERIOR: qué se apostó y qué pasó", correr("infra/estado/termometro.py", slug, "--revisar")),
        ("QUÉ FORMATO, TIPO DE IDEA Y AUTOR FUNCIONAN CON ESTE CLIENTE",
         correr("infra/estado/termometro.py", slug, "--ideas")),
        ("LO MISMO CRUZANDO TODOS LOS CLIENTES", correr("infra/estado/termometro.py", "--ideas")),
        ("QUÉ PLANTILLA (MECÁNICA) FUNCIONA CON ESTE CLIENTE",
         correr("infra/estado/termometro.py", slug, "--plantillas")),
        ("PANEL «QUÉ VÍDEOS HACER» — este cliente: haz más / evita / mejores y peores (nota = "
         "vistas + interacción frente a lo normal del cliente)", leer(HUB, "memoria/analisis", f"{slug}.md")),
        ("PANEL — LO QUE FUNCIONA EN TODA LA AGENCIA (apuesta por lo ganador que este cliente "
         "aún no ha probado; lo marcado 'solo en un cliente' es menos seguro)",
         leer(HUB, "memoria/analisis/general.md")),
        ("CREADORES DE REFERENCIA DE ESTE CLIENTE — úsalos como modelo: copia la MECÁNICA de su "
         "mejor vídeo (no el tema) y, si ves encaje, propone en Notas creadores parecidos para seguir",
         leer(HUB, "memoria/analisis/creadores", f"{slug}.md")),
        ("MÉTRICAS DE METRICOOL", leer(HUB, "memoria/metricas", f"{slug}.md")),
        ("FICHA DEL CLIENTE", leer(base_cli, "ficha.md")),
        ("BRIEF DE COPY (reglas duras de marca)", leer(base_cli, "copy-brief.md")),
        ("APRENDIZAJES (lo último)", leer(HUB, "memoria/aprendizajes/registro.md", limite=12000)),
        ("CATÁLOGO DE PLANTILLAS", leer(PLANTILLAS, "README.md")),
        ("RESTRICCIONES HEREDADAS DE LA TANDA ANTERIOR", "\n".join(f"- {r}" for r in restricciones_previas(slug))),
        ("LO QUE GERARD YA TUMBÓ Y POR QUÉ — no lo repitas ni lo disfraces",
         "\n".join(descartadas) or "(nada descartado todavía)"),
        ("IDEAS QUE YA ESTÁN EN MARCHA — no las dupliques", "\n".join(en_marcha) or "(ninguna)"),
    ]
    contexto = "\n\n".join(f"=== {t} ===\n{c or '(vacío)'}" for t, c in bloques)
    return (
        f"Eres Oli, la estratega de RM Agency. Monta la tanda del ciclo {mes} para **{label}** "
        f"(`{slug}`). Trabajas SOLA, de madrugada: nadie te va a contestar preguntas. Gerard verá "
        "cada idea en Notion y la aprobará o la descartará con un motivo.\n\n"
        f"{contexto}\n\n"
        "=== CÓMO TIENE QUE SALIR ===\n"
        "- 8 piezas DELIBERADAMENTE distintas. No se busca que funcionen las 8: se busca saber cuál funciona.\n"
        "- Con el termómetro delante: EXPLOTA lo que gana con 3+ piezas, REPITE lo que ganó con 1-2 "
        "(aún no concluye) y dedica 1-2 piezas a un formato o tipo de idea SIN PROBAR.\n"
        "- REPETIR GANADORES ES EL TRABAJO (regla de Gerard, 22/09/2026), con dos condiciones: "
        "(a) espáciado — un formato o una idea que ganó NO se repite en la tanda siguiente del "
        "mismo cliente, deja pasar al menos una tanda; (b) variantes, no calcos — mismo formato "
        "con otro tema, misma idea con otro formato, mismo ángulo en otro producto u objeción. "
        "En el `porque` di de qué ganador sale ('variante de <pieza>, x2,4 el 14/08'). Mira "
        "'IDEAS QUE YA ESTÁN EN MARCHA' y la tanda anterior para saber qué se usó hace nada.\n"
        "- Una pieza de control (etiqueta `control`): la que crees que va a fallar, para cerrar una discusión.\n"
        "- Cada pieza pasa el filtro de restricciones (§3 de tu ficha) y las reglas del brief.\n"
        "- `apuesta` falsable. `porque` cita una medición, un aprendizaje con fecha, o dice "
        "literalmente \"sin evidencia — apuesta ciega\". Nunca lo maquilles.\n"
        "- `titulo` = la idea en una frase que Gerard entienda sin abrir nada (es lo que verá en Notion).\n"
        "- NO inventes datos del cliente (productos, precios, nombres). Si falta uno, dilo en `datos_que_faltan`.\n"
        f"- `plantilla`: una de [{', '.join(plantillas())}].\n"
        f"- `formato` (QUÉ FORMA TIENE): una de [{', '.join(opciones.get(ei.PROP_FORMATO, []))}].\n"
        f"- `tipo_idea` (DE QUÉ VA): una de [{', '.join(opciones.get(ei.PROP_TIPO, []))}].\n"
        "LISTAS CERRADAS (02/10/2026): usa solo esas opciones, tal cual. **No inventes ninguna**; "
        "si ninguna encaja, deja \"\" y apúntalo en `datos_que_faltan`. Cada columna responde una "
        "pregunta distinta y no se solapan (tipo = de qué va · formato = qué forma tiene · "
        "plantilla = cómo se escribe el guion). Desempates: agentes/guiones/ETIQUETAS.md.\n"
        "- `tipo`: Viral o Marca. `soporte`: Reel, Carrusel o Story.\n\n"
        "Devuelve SOLO este JSON, sin texto alrededor ni ```:\n"
        '{"objetivo": "qué se quiere aprender de esta tanda", "restricciones": ["..."], '
        '"riesgos": "en qué te puedes estar equivocando", "datos_que_faltan": ["..."], '
        '"descartadas": [{"idea": "...", "motivo": "..."}], '
        '"piezas": [{"titulo": "...", "tipo": "Marca", "soporte": "Reel", "plantilla": "...", '
        '"formato": "...", "tipo_idea": "...", "apuesta": "...", "porque": "...", "etiquetas": []}]}'
    )


def llamar(prompt):
    proc = subprocess.run(
        ["claude", "-p", "--model", MODELO, "--tools", "", "--disable-slash-commands",
         "--no-session-persistence", "--max-budget-usd", PRESUPUESTO_USD, "--output-format", "json"],
        input=prompt, capture_output=True, text=True, timeout=600)
    try:
        d = json.loads(proc.stdout)
    except Exception:  # noqa: BLE001
        raise RuntimeError(f"claude salió {proc.returncode}: {proc.stderr[:300] or 'sin detalle'}")
    if proc.returncode != 0 or d.get("is_error") or d.get("subtype") != "success":
        raise RuntimeError(f"claude: {d.get('terminal_reason') or d.get('subtype')} {str(d.get('result'))[:200]}")
    t = (d.get("result") or "").strip()
    ini, fin = t.find("{"), t.rfind("}")
    if ini == -1:
        raise RuntimeError("Oli no devolvió JSON")
    return json.loads(t[ini:fin + 1])


def limitar_nuevas(piezas, opciones):
    """Deja en formato/tipo solo valores que existan en la lista de la base; el resto, vacío.

    Las listas son CERRADAS desde el 02/10/2026 (`agentes/guiones/ETIQUETAS.md`). Antes se
    dejaba pasar una etiqueta nueva por tanda y así nació el caos que hubo que limpiar: Humor en
    dos columnas, Receta en dos, tres opciones distintas para "lista".
    """
    for prop, clave in ((ei.PROP_FORMATO, "formato"), (ei.PROP_TIPO, "tipo_idea")):
        for pz in piezas:
            valor, fuera_de_lista = ei.casar(pz.get(clave) or "", opciones.get(prop, []))
            pz[clave] = None if (fuera_de_lista or not valor) else valor


def guardar_tanda(slug, mes, salida):
    """Escribe/fusiona `hipotesis.json`. Coco puede haber abierto ya el archivo al guionizar."""
    ruta = ruta_tanda(slug, mes)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    datos = cargar(ruta) or {"cliente": slug, "ciclo": mes, "piezas": []}
    for k in ("objetivo", "restricciones", "riesgos", "datos_que_faltan", "descartadas"):
        if salida.get(k):
            datos[k] = salida[k]
    corto = "".join(p[0] for p in slug.split("-"))
    validas = set(plantillas())
    nuevas = 0
    for pz in (salida.get("piezas") or [])[:10]:
        if not (pz.get("titulo") or "").strip():
            continue
        nuevas += 1
        datos.setdefault("piezas", []).append({
            "id": f"{corto}-{mes[-2:]}-oli{nuevas}",
            "titulo": pz["titulo"].strip()[:200],
            "tipo": pz.get("tipo") if pz.get("tipo") in ("Viral", "Marca") else None,
            "soporte": pz.get("soporte"),
            "plantilla": pz.get("plantilla") if pz.get("plantilla") in validas else None,
            "formato": (pz.get("formato") or "").strip() or None,
            "tipo_idea": (pz.get("tipo_idea") or "").strip() or None,
            "apuesta": pz.get("apuesta"), "porque": pz.get("porque"),
            "etiquetas": pz.get("etiquetas") or [], "autor": "Oli",
            "publicado": None, "resultado": None,
        })
    datos["oli_auto"] = {"generado": f"{datetime.datetime.now():%Y-%m-%d %H:%M}", "piezas": nuevas}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return datos, nuevas


def avisar(msg, asunto):
    try:
        subprocess.run([NOTIFY, msg, "OLI", "normal", "wa+email", asunto], timeout=120)
    except Exception:  # noqa: BLE001
        pass


def apuntar_inbox(texto):
    try:
        with open(INBOX, "a", encoding="utf-8") as f:
            f.write(f"\n- ⚠️ {datetime.datetime.now():%Y-%m-%d %H:%M} · oli_noche: {texto}\n")
    except OSError:
        pass


def clientes_en_analizar(hoy, cfg):
    return [s for s in cfg["clientes"] if (ciclo.fase_de(s, hoy) or {}).get("id") == "analizar"]


def generar(a, cfg, tok):
    hoy = datetime.date.today()
    mes = f"{hoy:%Y-%m}"
    objetivo = [a.cliente] if a.cliente else clientes_en_analizar(hoy, cfg)
    if not objetivo:
        print("Hoy no le toca Analizar a nadie.")
        return 0
    pendientes = pendientes_oli(cfg, tok)
    for slug in objetivo:
        label = cfg["clientes"][slug]["label"]
        if ya_hecha(slug, mes) and not a.forzar:
            print(f"· {label}: la tanda de {mes} ya está hecha.")
            continue
        # FRENO (Gerard, 02/10/2026): las ideas no se acumulan. Si queda alguna de Oli sin
        # revisar para este cliente, no se genera otra tanda — se le recuerda. Ni --forzar
        # lo salta: para eso está olivia.sh, la sesión a mano.
        if pendientes.get(slug):
            n_pend = pendientes[slug]
            print(f"⏸ {label}: {n_pend} ideas de Oli sin revisar — no genero más hasta que las revises.")
            if not (a.dry_run or a.prueba):
                avisar(f"⏸ Oli no ha preparado ideas nuevas para {label}: siguen {n_pend} sin revisar "
                       f"de la tanda anterior. Apruébalas o descártalas y la próxima vez salen nuevas.\n\n"
                       f"👉 {VISTA_OLI}",
                       f"[RM] Oli en pausa para {label}: {n_pend} ideas sin revisar")
            continue
        prompt = construir_prompt(slug, label, mes, tok, cfg)
        if a.dry_run:
            print(f"(dry-run) {label}: generaría la tanda de {mes} (prompt {len(prompt) // 1000} KB)")
            continue
        try:
            salida = llamar(prompt)
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
            if a.prueba:
                print(f"✗ {label}: {e}")
                continue
            apuntar_inbox(f"{label}: Oli no pudo montar la tanda ({e})")
            avisar(f"⚠️ Oli no ha podido montar la tanda de {label} esta noche: {e}\n"
                   f"Se puede lanzar a mano: infra/olivia/olivia.sh {slug}",
                   f"[RM] Oli: fallo en la tanda de {label}")
            continue
        if a.prueba:
            limitar_nuevas(salida.get("piezas") or [], ei.opciones(cfg["clientes"][slug]["database_id"], tok))
            print(json.dumps(salida, ensure_ascii=False, indent=1))
            continue
        limitar_nuevas(salida.get("piezas") or [], ei.opciones(cfg["clientes"][slug]["database_id"], tok))
        datos, n = guardar_tanda(slug, mes, salida)
        r = subprocess.run([PY, os.path.join(HUB, "infra/olivia/a_bandeja.py"), slug, mes],
                           capture_output=True, text=True, timeout=300)
        print(r.stdout.strip())
        piezas = [p for p in datos["piezas"] if p.get("autor") == "Oli"][-n:]
        lineas = "\n".join(f"• {p['titulo']}  ({p.get('formato') or '—'} · {p.get('tipo_idea') or '—'})"
                           for p in piezas)
        ciegas = sum(1 for p in piezas if "apuesta ciega" in (p.get("porque") or "").lower())
        avisar(f"🤖 Oli ha preparado {n} ideas para {label}. Hay que revisarlas.\n\n{lineas}\n\n"
               f"{ciegas} son apuestas ciegas (sin datos detrás).\n\n"
               "Apruébalas o descártalas en Notion antes del domingo (el lunes empiezan los "
               "guiones). Si descartas una, escribe el motivo en Notas: Oli lo lee el mes que viene.\n\n"
               f"👉 {VISTA_OLI}",
               f"[RM] Oli ha preparado {n} ideas para {label} — a revisar")
        print(f"✓ {label}: {n} ideas en la Bandeja")
    return 0


def pendientes_oli(cfg, tok):
    """{cliente: nº de ideas de Oli que siguen en Nueva} — sin revisar por Gerard."""
    filtro = {"and": [{"property": "Autor", "select": {"equals": "Oli"}},
                      {"property": "Estado", "select": {"equals": "Nueva"}}]}
    por_cliente = {}
    for f in na.query(cfg["bandeja"]["database_id"], tok, filtro):
        c = na.plain(f["properties"].get("Cliente")) or "?"
        por_cliente[c] = por_cliente.get(c, 0) + 1
    return por_cliente


def recordatorio(cfg, tok):
    """Sábado: ideas de Oli que siguen en Nueva. Solo avisa si hay algo."""
    por_cliente = pendientes_oli(cfg, tok)
    if not por_cliente:
        print("Nada de Oli pendiente de revisar.")
        return 0
    lbl = lambda s: cfg["clientes"].get(s, {}).get("label", s)  # noqa: E731
    resumen = "\n".join(f"• {lbl(c)}: {n}" for c, n in por_cliente.items())
    avisar(f"⏰ Quedan ideas de Oli sin revisar:\n\n{resumen}\n\nEl lunes empiezan los guiones: "
           f"lo que no esté aprobado no se guioniza.\n\n👉 {VISTA_OLI}",
           "[RM] Recordatorio: ideas de Oli sin revisar")
    print(resumen)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Oli sola: tanda mensual en la semana de Analizar.")
    ap.add_argument("--cliente")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--forzar", action="store_true", help="Aunque ya haya tanda este mes.")
    ap.add_argument("--recordatorio", action="store_true")
    ap.add_argument("--prueba", action="store_true",
                    help="Llama a Oli e imprime la tanda, pero NO escribe nada ni avisa.")
    a = ap.parse_args()
    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()
    if a.cliente and a.cliente not in cfg["clientes"]:
        sys.stderr.write(f"Cliente desconocido: {a.cliente}\n")
        return 1
    return recordatorio(cfg, tok) if a.recordatorio else generar(a, cfg, tok)


if __name__ == "__main__":
    raise SystemExit(main())
