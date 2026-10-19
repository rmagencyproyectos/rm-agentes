#!/usr/bin/env python3
"""Coco guioniza de madrugada las ideas marcadas "Coco a guionizar".

Al darle al botón ⚡ en Notion (o poner el desplegable a mano), la idea queda con
`Guion = Coco a guionizar`. Este script, que corre de noche (LaunchAgent
`com.rmagency.notion-noche`, 00:45, detrás del check-in), recorre las 6 bases de cliente y por
cada idea así marcada:

  1. la pone en `Guion = Guionando…` (para que no la coja otra corrida)
  2. monta el prompt de Coco: espina común (`agentes/guiones/_comun.md`) + el Tipo
     (`viral.md`/`marca.md`, el objetivo) + la **Plantilla** (`agentes/guiones/plantillas/`,
     la mecánica) + el brief y las métricas del cliente
  3. llama a `claude -p` sin herramientas (barato) y le pide SOLO un JSON
     (plantilla, gancho, palanca[], beats[], cta, copy_rrss, apuesta, porque, etiquetas[],
     notas_rodaje)
  4. escribe las propiedades (Gancho/Palanca/CTA/Plantilla/Copy RRSS) + el cuerpo del guion
  5. apunta la pieza en `ciclos/YYYY-MM/<cliente>/hipotesis.json` (el termómetro)
  6. deja `Guion = Listo`  → la idea sale de la vista ✍️ y entra en 🎬 A grabar

El **copy de redes viene en la misma pasada** (26/08/2026): antes lo escribía `autoprogramar.py`
semanas después, con el título como única fuente. Ahora Coco lo entrega con el guion y lo deja en
`Copy RRSS`; al programar se reutiliza y solo se genera si está vacío. Se escribe desde la IDEA y
las NOTAS de Gerard, **no** desde los beats: el guion lo va a retocar él antes de grabar, la idea
ya está dada por buena (regla en `agentes/guiones/_comun.md`).

Las **dos capas** (13/08/2026): `Tipo` dice a qué juega la pieza; `Plantilla` dice cómo se
cuenta. Solo la segunda se puede comparar contra otra, y por eso se guarda: sin ella el
termómetro medía vídeos sueltos y no podía decir qué formato funciona. Si la idea ya trae
Plantilla, se respeta; si no, Coco elige del catálogo y la declara.

Si algo falla (claude cae, JSON ilegible, sin brief): la idea VUELVE a "Coco a guionizar"
(nunca se queda colgada en "Guionando…") y se apunta la incidencia en INBOX-GERARD.md.

**Multicanal (19/10/2026)** — si la idea es de RM y trae `Soporte = Multicanal`, no se pide un guion
de vídeo: Coco devuelve en una sola llamada el carrusel como datos + copy IG/TikTok/FB + post de
LinkedIn + artículo de blog (`agentes/guiones/multicanal.md`). Se valida contra el brief de RM
(`infra/carruseles/multicanal.py`), se renderiza con `infra/carruseles/carrusel.py` en
`memoria/clientes/rm-agency/carruseles/<NN>-<id>/` y todo se cuelga en la ficha. Nada se publica.

**"Falta desglose" (26/08/2026)** — caso aparte, y el más frecuente: Coco no puede abrir un
enlace de Instagram/TikTok. Si la idea solo trae el link pelado, la ficha se aparca en
`Guion = "Falta desglose"` — no vuelve a la cola, no se reintenta cada noche y sale agrupada en
el panel **🖊️ Falta desglose** de `Agencia Marketing`, para poder escribirlas todas del tirón.
Basta con escribir las 2-3 líneas en `Notas`: la corrida siguiente las recoge sola
(`recuperadas()`), sin tocar el desplegable.

Se apoya en que el .sh que lo lanza ya exportó PATH y CLAUDE_CODE_OAUTH_TOKEN (ver noche.sh).

Uso:  guionizar.py [--cliente <slug>] [--max N] [--dry-run] [--modelo <id>]
Salida: 0 ok · 2 falta token Notion · 1 error
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

import etiquetas_idea as ei
import notion_api as na

HUB = na.HUB
GUIONES = os.path.join(HUB, "agentes/guiones")
PLANTILLAS = os.path.join(GUIONES, "plantillas")
CICLOS = os.path.join(HUB, "ciclos")
INBOX = os.path.join(HUB, "INBOX-GERARD.md")
MODELO_DEFECTO = "claude-sonnet-5"       # guion creativo: calidad > coste
# ⚠️ Tope por idea. Subido de 0.25 → 0.60 el 14/08/2026: al pasar de 2 plantillas a 13, el
# prompt creció a ~54 KB (el catálogo entero va dentro cuando la idea no trae Plantilla) y el
# coste real se puso en 0.255 — dos céntimos por encima del tope, y la idea moría con
# `budget_exhausted` sin decir por qué. Mismo patrón que el check-in de Winston.
# Truco de coste: **si la idea ya trae Plantilla asignada** (Oli normalmente la pone), solo va
# esa plantilla al prompt y la llamada sale mucho más barata.
PRESUPUESTO_USD = "0.60"                  # por idea
sys.path.insert(0, os.path.join(na.HUB, "infra/analisis"))
import etiquetas as _etq  # noqa: E402  — lee las listas de agentes/guiones/ETIQUETAS.md
sys.path.insert(0, os.path.join(na.HUB, "infra/carruseles"))
import multicanal as mc  # noqa: E402  — Soporte = Multicanal (solo RM)
SOPORTE_MULTICANAL = "Multicanal"
CLIENTE_MULTICANAL = "rm-agency"
# Una llamada da carrusel + copy + LinkedIn + blog (~5k tokens de salida): más tiempo, mismo tope.
PRESUPUESTO_MULTICANAL_USD = "0.60"
TIMEOUT_MULTICANAL = 300
PALANCAS = set(_etq.listas()["Palanca"])   # fuente: ETIQUETAS.md (sin Emoción ni Humor desde el 02/10/2026)
METODOLOGIAS = {"valor-directo", "bucle-abierto"}
COMPARTIBLE = {"Identidad", "Utilidad", "Plan", "Desahogo", "ninguno"}
# Plantillas de viral que NO se pueden escribir a ciegas: necesitan que Gerard haya desglosado
# la referencia a mano. Coco no puede abrir un enlace de Instagram (comprobado 14/08/2026:
# devuelve vacío siempre) ni ver un vídeo, así que guionizar esto sin desglose es inventárselo.
EXIGEN_DESGLOSE = {"replica-referencia"}
# Cuando la idea NO trae Plantilla, el gate de arriba no salta: Coco lee el catálogo, elige
# `replica-referencia` ella sola y se niega EN PROSA ("no puedo abrir el enlace…"). Eso llegaba
# como `no encontré JSON en la respuesta`, que parece una avería y no lo es: es Coco pidiendo el
# desglose. Estas pistas lo reconocen para aparcar la ficha en "Falta desglose" igual que el gate.
# (Diagnosticado el 26/08/2026 reproduciendo la llamada a mano.)
PISTAS_DESGLOSE = ("desglose", "no puedo abrir", "no tengo acceso", "no se guioniza",
                   "no puedo ver el", "necesito que me des")


def parece_falta_desglose(texto):
    """¿La respuesta sin JSON es Coco pidiendo el desglose, en vez de un fallo de verdad?"""
    t = (texto or "").lower()
    return any(pista in t for pista in PISTAS_DESGLOSE)


def leer(*partes):
    ruta = os.path.join(*partes)
    try:
        with open(ruta, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def plantillas_disponibles():
    try:
        return sorted(f[:-3] for f in os.listdir(PLANTILLAS)
                      if f.endswith(".md") and not f.startswith(("_", "README")))
    except OSError:
        return []


def bloque_plantillas(elegida):
    """El texto de plantilla que va al prompt.

    Si la idea ya trae `Plantilla` puesta (la eligió Oli o Gerard), va SOLO esa: la decisión
    ya está tomada y no se rediscute. Si viene vacía, van todas y Coco elige y lo declara —
    sale más caro en tokens, pero es la diferencia entre elegir la mecánica y caer siempre en
    la misma por inercia.
    """
    if elegida:
        txt = leer(PLANTILLAS, f"{elegida}.md")
        if txt:
            return f"=== PLANTILLA ASIGNADA: {elegida} (úsala, no la discutas) ===\n{txt}"
    partes = ["=== CATÁLOGO DE PLANTILLAS — elige UNA y declárala en el JSON ==="]
    for n in plantillas_disponibles():
        partes.append(f"\n--- {n} ---\n{leer(PLANTILLAS, f'{n}.md')}")
    return "\n".join(partes)


def contexto_cliente(slug):
    """Brief + ficha + métricas del cliente. Lo que exista; si falta, cadena vacía."""
    base = os.path.join(HUB, "memoria/clientes", slug)
    partes = []
    for nombre in ("copy-brief.md", "ficha.md"):
        txt = leer(base, nombre)
        if txt:
            partes.append(f"### {nombre}\n{txt}")
    metr = leer(HUB, "memoria/metricas", f"{slug}.md")
    if metr:
        partes.append(f"### métricas Metricool recientes\n{metr}")
    return "\n\n".join(partes) or "(sin brief todavía; usa el tono estándar del cliente)"


def bloque_etiquetas(opciones, ya):
    """Tipo de idea y Formato del contenido (etiquetas_idea.py). Si ya vienen puestas, no se tocan.

    Van con las opciones LEÍDAS EN VIVO de la base del cliente: si Gerard añade una en Notion,
    Coco la ve esa misma noche sin que nadie toque este archivo.
    """
    lineas = ["=== ETIQUETAS DE LA IDEA (se miden: clasifica con honestidad) ==="]
    for prop, clave in ((ei.PROP_TIPO, "tipo_idea"), (ei.PROP_FORMATO, "formato")):
        if ya.get(clave):
            lineas.append(f"- {prop}: YA PUESTA = {ya[clave]} (devuélvela igual)")
        else:
            lineas.append(f"- {prop}: elige UNA de [{', '.join(opciones.get(prop, [])) or '—'}]")
    lineas.append(
        "Clasifica lo que la pieza ES, no lo que convendría que fuera: esto se cruza con las\n"
        "vistas reales, y una etiqueta puesta por estrategia estropea la medición.\n"
        "LISTAS CERRADAS (02/10/2026): usa SOLO las opciones de arriba, tal cual están escritas.\n"
        "No inventes ninguna: si ninguna encaja, deja la cadena vacía. Qué va en cada columna y\n"
        "los desempates, en agentes/guiones/ETIQUETAS.md.")
    return "\n".join(lineas)


def construir_prompt(idea_titulo, tipo, notas, slug, label, plantilla=None, etiquetas=""):
    comun = leer(GUIONES, "_comun.md")
    tipo_md = leer(GUIONES, "viral.md" if tipo == "Viral" else "marca.md")
    ctx = contexto_cliente(slug)
    return (
        f"Eres Coco, la copywriter de RM Agency. Guioniza esta idea para **{label}**.\n\n"
        f"IDEA: {idea_titulo}\n"
        f"TIPO: {tipo or 'Marca'}\n"
        f"NOTAS: {notas or '(ninguna)'}\n\n"
        f"=== ESPINA DORSAL DEL GUION ===\n{comun}\n\n"
        f"=== TIPO (el objetivo) ===\n{tipo_md}\n\n"
        f"{bloque_plantillas(plantilla)}\n\n"
        f"{etiquetas}\n\n"
        f"=== CLIENTE ===\n{ctx}\n\n"
        "REGLA DURA — el `copy_rrss` se escribe desde la IDEA y las NOTAS de arriba, NO desde\n"
        "los beats ni el gancho que acabas de inventar. El guion lo va a retocar Gerard antes de\n"
        "grabar; la idea que ha escrito él ya está dada por buena. Si el copy sale del guion, se\n"
        "queda desfasado en cuanto se toque una frase. Detalle en la espina dorsal.\n\n"
        "REGLA DURA DE GERARD — el `copy_rrss` es CORTO: 25-50 palabras de cuerpo sin contar\n"
        "hashtags (manda sobre la longitud del brief). Palabra clave principal (SEO) en la\n"
        "primera línea. Y NO repite nada de lo que se dice o se ve en el vídeo: revisa tu\n"
        "`gancho` y tus `beats` y no pongas en el copy ninguna de esas ideas; aporta lo que el\n"
        "vídeo no dice (el porqué, contexto, un dato, la pregunta que deja abierta).\n\n"
        "REGLA DURA — no inventes datos del cliente. Nombres de local, marcas, productos,\n"
        "precios, horarios y cifras: o salen de la ficha/las notas de arriba, o NO se escriben.\n"
        "Si te falta un dato para que la pieza funcione, no te lo inventes: pídelo en\n"
        "`notas_rodaje` ('hace falta el gramaje real por tanda'). Una pieza con un dato\n"
        "inventado se graba mal y hay que repetirla.\n\n"
        "Devuelve SOLO el JSON especificado en la espina dorsal, sin ```json ni texto alrededor."
    )


def llamar_coco(prompt, modelo, system_prompt=None, presupuesto=PRESUPUESTO_USD, timeout=180):
    """Llama a claude -p sin herramientas y devuelve el texto (el JSON de Coco). Lanza si falla."""
    cmd = ["claude", "-p",
           "--model", modelo,
           "--tools", "",
           "--disable-slash-commands",
           "--no-session-persistence",
           "--max-budget-usd", presupuesto,
           "--output-format", "json"]
    if system_prompt:
        cmd += ["--system-prompt", system_prompt]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        # `claude` puede salir !=0 con el stderr VACÍO y el motivo real en el JSON de stdout
        # (p. ej. terminal_reason=budget_exhausted). Sin mirar ahí, el fallo sale mudo y se
        # confunde con un problema de red — pasó el 14/08/2026 y costó un rato averiguarlo.
        motivo = proc.stderr[:300].strip()
        try:
            d = json.loads(proc.stdout)
            motivo = (d.get("terminal_reason") or d.get("subtype")
                      or str(d.get("result"))[:200] or motivo)
            if d.get("total_cost_usd"):
                motivo += f" (coste {d['total_cost_usd']:.3f} / tope {presupuesto})"
        except Exception:  # noqa: BLE001
            pass
        raise RuntimeError(f"claude salió {proc.returncode}: {motivo or 'sin detalle'}")
    try:
        d = json.loads(proc.stdout)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"respuesta de claude ilegible: {e}")
    if d.get("is_error") or d.get("subtype") != "success":
        raise RuntimeError(f"claude error: {d.get('subtype')} {str(d.get('result'))[:200]}")
    return (d.get("result") or "").strip()


def parsear_guion(texto):
    """Extrae el JSON del guion aunque venga envuelto en ```json o con texto alrededor."""
    t = texto.strip()
    if "```" in t:
        # quedarse con lo que hay entre la primera y la última llave
        pass
    ini, fin = t.find("{"), t.rfind("}")
    if ini == -1 or fin == -1:
        raise RuntimeError("no encontré JSON en la respuesta")
    d = json.loads(t[ini:fin + 1])
    gancho = (d.get("gancho") or "").strip()
    beats = d.get("beats") or []
    cta = (d.get("cta") or "").strip()
    if not gancho or not beats:
        raise RuntimeError("JSON sin gancho o sin beats")
    palanca = [p for p in (d.get("palanca") or []) if p in PALANCAS]
    # Plantilla y metodología tienen que ser de las que existen: si Coco se inventa un nombre,
    # la pieza queda fuera de la comparativa del termómetro sin que nadie lo note.
    plantilla = (d.get("plantilla") or "").strip()
    if plantilla and plantilla not in plantillas_disponibles():
        plantilla = ""
    metodologia = (d.get("metodologia") or "").strip()
    if metodologia not in METODOLOGIAS:
        metodologia = ""
    compartible = (d.get("compartible") or "").strip().capitalize()
    if compartible not in COMPARTIBLE:
        compartible = "ninguno" if compartible.lower() == "ninguno" else ""
    return {
        "plantilla": plantilla,
        "metodologia": metodologia,
        "gancho": gancho,
        "palanca": palanca,
        "beats": [str(b) for b in beats],
        "cta": cta,
        "copy_rrss": (d.get("copy_rrss") or "").strip(),
        "compartible": compartible,
        "valor_gratis": (d.get("valor_gratis") or "").strip(),
        "apuesta": (d.get("apuesta") or "").strip(),
        "porque": (d.get("porque") or "").strip(),
        "etiquetas": [str(e) for e in (d.get("etiquetas") or [])][:6],
        "tipo_idea": str(d.get("tipo_idea") or "").strip(),
        "formato": str(d.get("formato") or d.get("estructura") or "").strip(),
        "notas_rodaje": (d.get("notas_rodaje") or "").strip(),
    }


def cuerpo_markdown(g):
    """Construye los bloques de la página con la plantilla fija del guion."""
    bloques = [
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": [{"text": {"content": "🎣 Gancho — 0-3s"}}]}},
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"text": {"content": g["gancho"][:1900]}}]}},
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": [{"text": {"content": "🔁 Retención — que no deslicen"}}]}},
    ]
    for b in g["beats"]:
        bloques.append({"object": "block", "type": "bulleted_list_item",
                        "bulleted_list_item": {"rich_text": [{"text": {"content": b[:1900]}}]}})
    bloques += [
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": [{"text": {"content": "📣 CTA"}}]}},
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"text": {"content": (g["cta"] or "—")[:1900]}}]}},
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": [{"text": {"content": "🎬 Rodaje"}}]}},
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"text": {"content": (g["notas_rodaje"] or "—")[:1900]}}]}},
    ]
    # La apuesta va en la ficha, no solo en el JSON del termómetro: si Gerard no la ve al
    # revisar la tarjeta, no puede corregirla antes de grabar — y corregirla después no sirve.
    if g["apuesta"] or g["porque"]:
        apuesta = f"{g['apuesta']}\n\nPor qué: {g['porque']}".strip()
        bloques += [
            {"object": "block", "type": "heading_2",
             "heading_2": {"rich_text": [{"text": {"content": "🎯 Qué estamos probando"}}]}},
            {"object": "block", "type": "paragraph",
             "paragraph": {"rich_text": [{"text": {"content": apuesta[:1900]}}]}},
        ]
    # El valor gratis y el motivo de compartición se enseñan porque son los dos filtros que
    # más fácil se saltan al revisar: una pieza que no da nada y que nadie reenviaría se ve
    # aquí en dos segundos, y no después de haberla rodado.
    linea = []
    if g["valor_gratis"]:
        linea.append(f"Se lleva: {g['valor_gratis']}")
    if g["compartible"]:
        linea.append(f"Se comparte por: {g['compartible']}"
                     + (" ⚠️ no cumple ninguno" if g["compartible"] == "ninguno" else ""))
    if linea:
        bloques.append({"object": "block", "type": "callout", "callout": {
            "icon": {"emoji": "🎁"},
            "rich_text": [{"text": {"content": " · ".join(linea)[:1900]}}]}})
    return bloques


# La primera cabecera que escribe Coco. Todo lo que hay de aquí hacia abajo es suyo, así que
# es el punto de corte seguro para re-guionizar sin tocar lo que haya escrito una persona
# encima de la ficha.
MARCA_INICIO = "🎣 Gancho"


def limpiar_guion_anterior(page_id, tok):
    """Borra el guion viejo antes de escribir el nuevo. Devuelve cuántos bloques quitó.

    Sin esto, re-guionizar deja los dos guiones pegados en la misma ficha y el resultado es
    ilegible. Se corta desde la primera cabecera de Coco hasta el final: lo que alguien haya
    escrito ARRIBA a mano se respeta.
    """
    bloques = na.list_blocks(page_id, tok)
    inicio = next((i for i, b in enumerate(bloques)
                   if na.texto_de_bloque(b).startswith((MARCA_INICIO, mc.MARCA_INICIO))), None)
    if inicio is None:
        return 0
    # De atrás hacia delante: así los índices no se mueven mientras se borra.
    for b in reversed(bloques[inicio:]):
        na.delete_block(b["id"], tok)
    return len(bloques) - inicio


def tiene_desglose(notas):
    """¿Las notas traen el desglose humano de la referencia, o solo el enlace pelado?

    Coco no puede abrir el vídeo, así que sin desglose lo único que puede hacer es inventarse
    un viral y llamarlo réplica. Se descarta lo que no aporta nada (URLs, la línea 'Referencia:'
    que mete distribuir.py) y se mira si queda descripción de verdad.
    """
    if not notas:
        return False
    limpio = re.sub(r"https?://\S+", "", notas)
    limpio = re.sub(r"(?i)^\s*referencia\s*:\s*$", "", limpio, flags=re.M)
    return len(limpio.strip()) >= 60


def apuntar_hipotesis(slug, titulo, g):
    """Añade la pieza a `ciclos/YYYY-MM/<cliente>/hipotesis.json` (el termómetro).

    Por qué automático: la regla del 11/08/2026 dice que ninguna pieza se produce sin
    hipótesis escrita, y dos días después salieron 8 piezas de Golossa sin ninguna. La regla
    existía pero nada la aplicaba, que es la peor combinación. Ahora la escribe quien tiene
    la información en la mano — Coco, en el momento de guionizar.

    Es idempotente por título: re-guionizar una idea actualiza su pieza, no la duplica.
    Best-effort: si esto falla, el guion ya está escrito en Notion y no se pierde nada.
    """
    try:
        ciclo = f"{datetime.date.today():%Y-%m}"
        ruta = os.path.join(CICLOS, ciclo, slug, "hipotesis.json")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        try:
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
        except (FileNotFoundError, ValueError):
            datos = {"cliente": slug, "ciclo": ciclo,
                     "objetivo": "Tanda abierta por Coco al guionizar. "
                                 "Revisa el objetivo y las restricciones a mano.",
                     "restricciones": [], "piezas": []}
        piezas = datos.setdefault("piezas", [])
        pieza = next((p for p in piezas if p.get("titulo") == titulo), None)
        if pieza is None:
            corto = "".join(p[0] for p in slug.split("-")) or slug[:2]
            pieza = {"id": f"{corto}-{ciclo[-2:]}-{len(piezas) + 1}", "titulo": titulo,
                     "publicado": None, "resultado": None}
            piezas.append(pieza)
        # Una pieza ya medida no se toca: reescribir su apuesta a posteriori invalidaría
        # justamente lo que el termómetro está midiendo.
        if pieza.get("resultado"):
            return
        pieza["plantilla"] = g["plantilla"]
        pieza["metodologia"] = g["metodologia"]
        pieza["compartible"] = g["compartible"]
        pieza["apuesta"] = g["apuesta"]
        pieza["porque"] = g["porque"]
        pieza["etiquetas"] = g["etiquetas"]
        pieza["tipo_idea"] = g.get("tipo_idea", "")
        pieza["formato"] = g.get("formato", "")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    except Exception as e:  # noqa: BLE001
        apuntar_inbox(f"{slug}/{titulo[:40]}: guion OK pero no pude apuntar la hipótesis ({e})")


def avisar_desglose(paradas):
    """Pide a Gerard el desglose de las réplicas paradas — de una en una, no en bloque.

    El patrón de las 11 referencias sin triar enseñó que enfrentarse a un montón de golpe es
    justo lo que hace que no se haga nunca. Aquí se le piden dos líneas por pieza concreta.
    """
    lineas = [f"• {lbl}: {(idea or '')[:60]}" for lbl, idea in paradas[:5]]
    resto = f"\n(y {len(paradas) - 5} más)" if len(paradas) > 5 else ""
    msg = ("🎬 No puedo guionizar esto: no puedo abrir la referencia y no sé qué pasa en el "
           "vídeo.\n\n" + "\n".join(lineas) + resto +
           "\n\nEscríbeme 2 líneas de cada una en las Notas: qué pasa, dónde está el giro y "
           "por qué funciona. Solo eso — no hace falta tocar el desplegable, se guionizan solas "
           "en la siguiente corrida.\n\nLas tienes todas juntas en el panel 🖊️ Falta desglose 🙌")
    notify = os.path.join(HUB, "infra/notifier/notify.sh")
    try:
        subprocess.run([notify, msg, "DESGLOSE", "normal"], timeout=60)
    except Exception:  # noqa: BLE001
        pass


def avisar_whatsapp(generadas, nuevas_opciones=()):
    """Manda a Gerard un WhatsApp (vía notify.sh) con las ideas guionadas y su enlace a Notion.

    El enlace `app.notion.com/p/<id>` abre la ficha en la app de Notion del móvil. Best-effort: si
    notify.sh falla (WA caído, etc.) la cascada ya cae a email/push/INBOX y no rompe la corrida.
    """
    lineas = [f"• {lbl}: {(idea or '')[:50]}\n  {url}" for lbl, idea, url in generadas]
    msg = (f"✍️ Coco guionó anoche {len(generadas)} idea(s), listas para grabar:\n\n"
           + "\n".join(lineas) + "\n\nToca el enlace para abrirla en Notion 📱")
    if nuevas_opciones:
        msg += ("\n\n🏷️ Etiquetas que he querido usar y no están en la lista (se han quedado "
                "sin poner):\n"
                + "\n".join(f"• {p}: {v} ({lbl})" for lbl, p, v in nuevas_opciones)
                + "\nSi alguna hace falta de verdad, dímelo y la añado a la lista.")
    notify = os.path.join(HUB, "infra/notifier/notify.sh")
    try:
        subprocess.run([notify, msg, "GUIONES", "normal"], timeout=60)
    except Exception:  # noqa: BLE001
        pass


def apuntar_inbox(texto):
    try:
        with open(INBOX, "a", encoding="utf-8") as f:
            f.write(f"\n- ⚠️ {datetime.datetime.now():%Y-%m-%d %H:%M} · guionizar: {texto}\n")
    except Exception:  # noqa: BLE001
        pass


def pendientes(cfg, tok, solo_cliente, estado="Coco a guionizar", titulos=None):
    """Ideas a guionizar. Con estado='Listo' saca las YA guionizadas (para re-guionizar)."""
    filtro = {"property": "Guion", "select": {"equals": estado}}
    items = []
    for slug, cli in cfg["clientes"].items():
        if solo_cliente and slug != solo_cliente:
            continue
        for f in na.query(cli["database_id"], tok, filtro):
            p = f["properties"]
            if titulos:
                idea = (na.plain(p.get("Idea")) or "").lower()
                if not any(t.lower() in idea for t in titulos):
                    continue
            items.append({
                "page_id": f["id"], "slug": slug, "label": cli["label"],
                "idea": na.plain(p.get("Idea")),
                "tipo": na.plain(p.get("Tipo")),
                "plantilla": na.plain(p.get("Plantilla")),
                "tipo_idea": na.plain(p.get(ei.PROP_TIPO)),
                "formato": ei.leer(p, ei.PROP_FORMATO, cli["database_id"], tok),
                "notas": na.plain(p.get("Notas")),
                "soporte": ei.leer(p, ei.PROP_SOPORTE, cli["database_id"], tok),
            })
    return items


def recuperadas(cfg, tok, solo_cliente):
    """Fichas paradas en "Falta desglose" a las que Gerard YA les ha escrito el desglose.

    Así solo tiene que escribir las 2-3 líneas en Notas: no hace falta que además se acuerde de
    volver a poner el desplegable en "Coco a guionizar". Si no ha escrito nada, la ficha sigue
    parada y no se gasta una llamada.
    """
    return [it for it in pendientes(cfg, tok, solo_cliente, "Falta desglose")
            if tiene_desglose(it["notas"])]


_PROPS_BASE = {}


def tiene_prop(database_id, tok, nombre):
    """¿Existe la propiedad en la base? (LinkedIn la tiene que crear Gerard: si no está, solo va al cuerpo)."""
    if database_id not in _PROPS_BASE:
        try:
            _PROPS_BASE[database_id] = set(na._request("GET", f"/databases/{database_id}", tok)
                                           .get("properties", {}))
        except RuntimeError:
            _PROPS_BASE[database_id] = set()
    return nombre in _PROPS_BASE[database_id]


def es_multicanal(it):
    return it.get("slug") == CLIENTE_MULTICANAL and (it.get("soporte") or "") == SOPORTE_MULTICANAL


def guionizar_multicanal(it, tok, cfg, modelo, reguionizar=False):
    """Soporte = Multicanal: carrusel + copy + LinkedIn + blog en una llamada. Devuelve (url, avisos).

    Lanza RuntimeError / TimeoutExpired si no sale: el bucle de main() devuelve la idea a la cola.
    """
    cifras = mc.cifras_de(it["idea"], it["notas"])
    prompt = mc.construir_prompt(it["idea"], it["notas"], cifras)
    kw = dict(system_prompt=mc.SYSTEM_PROMPT, presupuesto=PRESUPUESTO_MULTICANAL_USD, timeout=TIMEOUT_MULTICANAL)
    crudo = llamar_coco(prompt, modelo, **kw)
    try:
        res = mc.parsear(crudo, cifras)
    except RuntimeError as e:
        # Una sola corrección en la misma corrida (p. ej. «Episodio 25» sin verificar): sale más
        # barato que devolver la idea a la cola y repetir la llamada entera mañana. Si vuelve a
        # fallar, se lanza y main() la devuelve a la cola con el motivo en el INBOX.
        print(f"   ↻ corrección: {e}")
        crudo = llamar_coco(mc.prompt_correccion(prompt, crudo, str(e)), modelo, **kw)
        res = mc.parsear(crudo, cifras)
    guardado = mc.guardar(res)          # textos + PNG + PDF en memoria/clientes/rm-agency/carruseles/
    if guardado["error_render"]:
        apuntar_inbox(f"[rm-agency] {it['idea'][:50]}: textos OK pero el carrusel no se pudo "
                      f"renderizar ({guardado['error_render'][:120]})")
    if reguionizar:
        limpiar_guion_anterior(it["page_id"], tok)
    na.append_blocks(it["page_id"], tok, mc.bloques_notion(res, guardado))
    db = cfg["clientes"][it["slug"]]["database_id"]
    props = {"Copy RRSS": na.prop_text(res["copy_ig"]), "Guion": na.prop_select("Listo")}
    if tiene_prop(db, tok, "LinkedIn"):
        props["LinkedIn"] = na.prop_text(res["linkedin"])
    na.update_props(it["page_id"], tok, props)
    apuntar_hipotesis(it["slug"], it["idea"], {
        "plantilla": "", "metodologia": "", "compartible": "", "apuesta": res["apuesta"],
        "porque": res["porque"], "etiquetas": ["multicanal", "carrusel"],
        "tipo_idea": it.get("tipo_idea") or "", "formato": it.get("formato") or ""})
    return "https://app.notion.com/p/" + it["page_id"].replace("-", ""), res["avisos"]


def main():
    ap = argparse.ArgumentParser(description="Coco guioniza las ideas marcadas 'Coco a guionizar'.")
    ap.add_argument("--cliente", help="Limita a un slug.")
    ap.add_argument("--max", type=int, default=10, help="Tope de guiones por corrida (coste).")
    ap.add_argument("--modelo", default=MODELO_DEFECTO)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--avisar", action="store_true",
                    help="Al terminar, manda a Gerard un WhatsApp con las ideas guionadas + enlace.")
    ap.add_argument("--reguionizar", action="store_true",
                    help="Rehace guiones YA escritos (Guion=Listo), borrando antes el viejo.")
    ap.add_argument("--titulo", action="append", metavar="TEXTO",
                    help="Solo las ideas cuyo título contenga TEXTO. Repetible.")
    a = ap.parse_args()

    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()

    estado = "Listo" if a.reguionizar else "Coco a guionizar"
    try:
        cola = pendientes(cfg, tok, a.cliente, estado, a.titulo)
    except RuntimeError as e:
        sys.stderr.write(f"No pude leer las bases: {e}\n")
        return 1

    if not a.reguionizar:
        try:
            vueltas = recuperadas(cfg, tok, a.cliente)
        except RuntimeError:
            vueltas = []
        if vueltas:
            print(f"{len(vueltas)} parada(s) con el desglose ya escrito: vuelven a la cola.")
            cola = vueltas + cola

    if not cola:
        print("Nada que re-guionizar." if a.reguionizar else "Nada que guionizar.")
        return 0
    cola = cola[:a.max]
    print(f"{len(cola)} ideas para guionizar (tope {a.max}).")

    hechas = 0
    generadas = []     # (label, idea, url) para el aviso por WhatsApp
    sin_desglose = []  # réplicas paradas esperando 2 líneas de Gerard
    nuevas_opciones = []  # (cliente, prop, valor) que Coco ha creado: se avisan, no se esconden
    opciones_cli = {}     # slug -> opciones en vivo de Tipo de idea / Formato (1 GET por cliente)
    for it in cola:
        etiqueta = f"[{it['slug']}] {(it['idea'] or '')[:60]}"

        # Gate: una réplica sin desglose humano no se guioniza, se pide. Se saca de la cola
        # (estado propio) para que no lo reintente cada noche en silencio.
        if it["plantilla"] in EXIGEN_DESGLOSE and not tiene_desglose(it["notas"]):
            if a.dry_run:
                print(f"(dry-run) PARARÍA por falta de desglose: {etiqueta}")
                continue
            na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Falta desglose")})
            apuntar_inbox(f"{etiqueta}: es una réplica y no tiene desglose. Escribe 2-3 líneas "
                          f"en Notas (qué pasa, dónde está el giro, por qué funciona) y se "
                          f"guioniza sola la próxima corrida.")
            sin_desglose.append((it["label"], it["idea"]))
            print(f"⏸ {etiqueta}: falta el desglose de la referencia")
            continue

        if a.dry_run:
            if es_multicanal(it):
                print(f"(dry-run) MULTICANAL: {etiqueta} → carrusel + copy + LinkedIn + blog")
                continue
            print(f"(dry-run) guionizaría: {etiqueta} ({it['tipo'] or 'Marca'} · "
                  f"plantilla: {it['plantilla'] or 'la elige Coco'})")
            continue
        # 1. marcar Guionando… para que no la coja otra corrida
        try:
            na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Guionando…")})
        except RuntimeError as e:
            sys.stderr.write(f"✗ {etiqueta}: no pude marcar Guionando ({e})\n")
            continue
        if es_multicanal(it):
            try:
                url, avisos = guionizar_multicanal(it, tok, cfg, a.modelo, a.reguionizar)
            except (RuntimeError, subprocess.TimeoutExpired) as e:
                na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Coco a guionizar")})
                apuntar_inbox(f"{etiqueta} (multicanal) no salió: {e}")
                sys.stderr.write(f"✗ {etiqueta}: multicanal {e} (devuelta a 'Coco a guionizar')\n")
                continue
            for x in avisos:
                print(f"   ⚠️ {x}")
            generadas.append((it["label"], it["idea"], url))
            print(f"✓ {etiqueta} (multicanal) :: {url}")
            hechas += 1
            continue
        # 2-3. pedir el guion a Coco
        try:
            if it["slug"] not in opciones_cli:
                try:
                    opciones_cli[it["slug"]] = ei.opciones(
                        cfg["clientes"][it["slug"]]["database_id"], tok)
                except RuntimeError:
                    opciones_cli[it["slug"]] = {}
            prompt = construir_prompt(it["idea"], it["tipo"], it["notas"], it["slug"],
                                      it["label"], it["plantilla"],
                                      bloque_etiquetas(opciones_cli[it["slug"]], it))
            crudo = llamar_coco(prompt, a.modelo)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Coco a guionizar")})
            apuntar_inbox(f"{etiqueta} no se pudo guionizar: {e}")
            sys.stderr.write(f"✗ {etiqueta}: {e} (devuelta a 'Coco a guionizar')\n")
            continue
        try:
            g = parsear_guion(crudo)
        except RuntimeError as e:
            # Coco contestando en prosa que le falta el desglose NO es un fallo: es una petición.
            # Va al mismo carril que el gate de arriba, para que salga en el panel y no se
            # reintente cada noche gastando una llamada para recibir el mismo "no".
            if parece_falta_desglose(crudo):
                na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Falta desglose")})
                apuntar_inbox(f"{etiqueta}: Coco no puede abrir la referencia. Escribe 2-3 líneas "
                              f"en Notas (qué pasa, dónde está el giro, por qué funciona) y se "
                              f"guioniza sola la próxima corrida.")
                sin_desglose.append((it["label"], it["idea"]))
                print(f"⏸ {etiqueta}: falta el desglose de la referencia")
                continue
            na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Coco a guionizar")})
            apuntar_inbox(f"{etiqueta} no se pudo guionizar: {e}")
            sys.stderr.write(f"✗ {etiqueta}: {e} (devuelta a 'Coco a guionizar')\n")
            continue
        # 4-5. escribir props + cuerpo + Listo
        try:
            if a.reguionizar:
                quitados = limpiar_guion_anterior(it["page_id"], tok)
                print(f"   ↳ guion anterior borrado ({quitados} bloques)")
            na.append_blocks(it["page_id"], tok, cuerpo_markdown(g))
            props = {
                "Gancho (0-3s)": na.prop_text(g["gancho"]),
                "CTA": na.prop_text(g["cta"]),
                "Palanca": na.prop_multi(g["palanca"]),
                "Guion": na.prop_select("Listo"),
            }
            if g["plantilla"]:
                props["Plantilla"] = na.prop_select(g["plantilla"])
            if g["metodologia"]:
                props["Metodologia"] = na.prop_select(g["metodologia"])
            if g["copy_rrss"]:
                props["Copy RRSS"] = na.prop_text(g["copy_rrss"])
            # Etiquetas de la idea: lo que puso una persona manda; Coco solo rellena huecos.
            for prop, clave in ((ei.PROP_TIPO, "tipo_idea"), (ei.PROP_FORMATO, "formato")):
                if it.get(clave):
                    g[clave] = it[clave]
                    continue
                valor, nuevo = ei.casar(g[clave], opciones_cli.get(it["slug"], {}).get(prop, []))
                # Listas cerradas: lo que no esté en la lista NO se crea, se descarta y se avisa.
                # La lista se amplía a mano en ETIQUETAS.md, no por invención de Coco.
                if nuevo:
                    nuevas_opciones.append((it["label"], prop, valor))
                    valor = ""
                g[clave] = valor
                if valor:
                    props[prop] = na.prop_select(valor)
            na.update_props(it["page_id"], tok,
                            ei.traducir(props, cfg["clientes"][it["slug"]]["database_id"], tok))
            apuntar_hipotesis(it["slug"], it["idea"], g)
            url = "https://app.notion.com/p/" + it["page_id"].replace("-", "")
            generadas.append((it["label"], it["idea"], url))
            print(f"✓ {etiqueta} :: {url}")
            hechas += 1
        except RuntimeError as e:
            na.update_props(it["page_id"], tok, {"Guion": na.prop_select("Coco a guionizar")})
            apuntar_inbox(f"{etiqueta}: guion generado pero no pude escribirlo en Notion: {e}")
            sys.stderr.write(f"✗ {etiqueta}: guion OK pero fallo al escribir ({e})\n")

    if nuevas_opciones:
        # No se deja crecer la lista a escondidas: una opción nueva es una categoría nueva que
        # partirá la medición en dos. Gerard la ve y decide si se queda o la fusiona.
        for lbl, prop, valor in nuevas_opciones:
            apuntar_inbox(f"Coco quiso poner «{valor}» en {prop} ({lbl}) y no está en la lista: "
                          f"la pieza se queda sin esa etiqueta. Si la opción hace falta, añádela "
                          f"a agentes/guiones/ETIQUETAS.md y siémbrala con etiquetas_idea.py.")
            print(f"✗ fuera de lista en {prop} ({lbl}): {valor} (descartada)")
    if a.avisar and generadas:
        avisar_whatsapp(generadas, nuevas_opciones)
    if a.avisar and sin_desglose:
        avisar_desglose(sin_desglose)
    if not a.dry_run:
        print(f"\nGuionadas {hechas}/{len(cola)} · {datetime.datetime.now():%Y-%m-%d %H:%M}")
        if sin_desglose:
            print(f"{len(sin_desglose)} paradas esperando desglose de la referencia.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
