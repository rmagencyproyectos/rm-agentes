#!/usr/bin/env python3
"""El termómetro: cruza lo que creíamos que iba a funcionar con lo que funcionó.

Cada pieza sale con una **hipótesis escrita** (`ciclos/YYYY-MM/<cliente>/hipotesis.json`).
Cuando se publica se le pone la fecha. Este script busca esa publicación en las métricas
reales y la compara con **lo normal de ese cliente en esa red**. No hay opiniones: hay
ratio contra su propia mediana.

Por qué mediana y no media: un solo reel viral (Golossa, julio) se lleva el 90% del mes y
deja la media inservible como listón. La mediana dice "una pieza corriente de este cliente".

Uso:
  termometro.py                          -> qué tandas hay abiertas y qué toca cerrar
  termometro.py <cliente> [--ciclo YYYY-MM]   -> el informe de esa tanda
  termometro.py <cliente> --cerrar       -> además guarda el resultado en hipotesis.json
  termometro.py <cliente> --etiquetas    -> qué funciona históricamente, por etiqueta
  termometro.py <cliente> --plantillas   -> qué MECÁNICA funciona con ese cliente
  termometro.py --plantillas             -> la misma comparativa, cruzando todos los clientes
  termometro.py [<cliente>] --formatos     -> qué FORMATO de contenido funciona (tips, top 10…)
  termometro.py [<cliente>] --tipos-idea   -> qué TIPO DE IDEA funciona (educativa, humor…)
  termometro.py [<cliente>] --autores      -> de quién son las ideas que funcionan (Gerard, Oli…)
  termometro.py [<cliente>] --ideas        -> las tres anteriores juntas (lo que lee Oli)

Formato, Tipo de idea y Autor son las etiquetas de `infra/notion/etiquetas_idea.py`. OJO:
aquí "formato" es el del CONTENIDO; Reel/Carrusel es `soporte` (y el listón ya lo separa).
Los agregados (`--ideas`, `--formatos`, `--tipos-idea`, `--autores`, `--plantillas`) miden desde las
piezas PUBLICADAS en Notion (`memoria/clasificacion/_piezas/`, lo deja `clasificacion.py` cada
noche), no desde `hipotesis.json`: los títulos de las tandas y los de Notion no casaban nunca,
y medir desde las tandas dejaba fuera todo lo publicado (comprobado el 22/09/2026).
"""
import datetime
import glob
import json
import os
import statistics
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
POSTS = os.path.join(HUB, "memoria/metricas/_posts")
CICLOS = os.path.join(HUB, "ciclos")
PIEZAS_NOTION = os.path.join(HUB, "memoria/clasificacion/_piezas")
NOMBRES = {"jesus-mora": "Jesús Mora", "xavi-colomina": "Xavi", "golossa": "Golossa",
           "midtown": "Midtown", "msm": "MSM", "newmos": "Newmos"}

# Días que necesita una pieza para poder juzgarla. Antes de eso el número aún se mueve
# (sobre todo en TikTok, que sigue repartiendo durante semanas).
DIAS_MADUREZ = 14
# Mínimo de publicaciones para fiarse de un listón de red+formato; por debajo, se usa
# el de la red entera.
MIN_MUESTRA = 4

# Ratio (vistas / listón) -> veredicto. De mejor a peor; se coge el primero que cumple.
ESCALA = [
    (2.0, "🟢🟢", "pegó"),
    (1.2, "🟢", "por encima"),
    (0.8, "⚪", "en su media"),
    (0.0, "🔴", "por debajo"),
]


def nombre(cli):
    return NOMBRES.get(cli, cli)


# ---------------------------------------------------------------- datos
def cargar_posts(cli):
    """Todas las publicaciones del cliente que trajo `fetch_metricool.py`."""
    try:
        with open(os.path.join(POSTS, f"{cli}.json"), encoding="utf-8") as f:
            return json.load(f).get("posts", [])
    except (OSError, ValueError):
        return []


def ruta_hipotesis(cli, ciclo):
    return os.path.join(CICLOS, ciclo, cli, "hipotesis.json")


def cargar_hipotesis(cli, ciclo):
    try:
        with open(ruta_hipotesis(cli, ciclo), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def ciclos_con_hipotesis(cli=None):
    """(cliente, ciclo) de cada tanda que existe, de la más reciente a la más vieja."""
    patron = os.path.join(CICLOS, "*", cli or "*", "hipotesis.json")
    out = []
    for ruta in glob.glob(patron):
        partes = ruta.split(os.sep)
        out.append((partes[-2], partes[-3]))
    return sorted(out, key=lambda x: x[1], reverse=True)


# ---------------------------------------------------------------- el listón
def liston(posts, fechas_excluidas):
    """Mediana de vistas por 'red · formato' y por red, sin contar la propia tanda.

    Si la tanda entrara en su propio listón se estaría comparando consigo misma: 8 vídeos
    nuevos moverían la mediana y todo saldría "normal".
    """
    por_grupo, por_red = {}, {}
    for p in posts:
        if p.get("fecha") in fechas_excluidas:
            continue
        por_grupo.setdefault(f"{p['red']} · {p['formato']}", []).append(p.get("vistas", 0))
        por_red.setdefault(p["red"], []).append(p.get("vistas", 0))
    med = lambda xs: int(statistics.median(xs)) if xs else 0  # noqa: E731
    return ({k: med(v) for k, v in por_grupo.items() if len(v) >= MIN_MUESTRA},
            {k: med(v) for k, v in por_red.items()})


def liston_de(post, grupos, redes):
    """Listón de una publicación: el de su formato si hay muestra, si no el de su red."""
    return grupos.get(f"{post['red']} · {post['formato']}") or redes.get(post["red"], 0)


def veredicto(ratio):
    for corte, emoji, texto in ESCALA:
        if ratio >= corte:
            return emoji, texto
    return "🔴", "por debajo"


# ---------------------------------------------------------------- evaluación
def evaluar(pieza, posts, grupos, redes, hoy):
    """Resultado de una pieza, o None si aún no se puede juzgar.

    El cruce es por **fecha de publicación**: un cliente publica una pieza al día, así que
    la fecha identifica la pieza. Si el mismo vídeo salió en Reels y en TikTok, cuentan las
    dos: se suman las vistas y se suman sus listones.
    """
    fecha = pieza.get("publicado")
    if not fecha:
        return None
    encontrados = [p for p in posts if p.get("fecha") == fecha]
    if not encontrados:
        return {"estado": "sin_datos"}
    try:
        dias = (hoy - datetime.date.fromisoformat(fecha)).days
    except ValueError:
        return {"estado": "sin_datos"}
    if dias < DIAS_MADUREZ:
        return {"estado": "verde", "dias": dias}
    vistas = sum(p.get("vistas", 0) for p in encontrados)
    esperado = sum(liston_de(p, grupos, redes) for p in encontrados)
    if not esperado:
        return {"estado": "sin_liston"}
    ratio = round(vistas / esperado, 2)
    emoji, texto = veredicto(ratio)
    return {"estado": "medido", "calculado": hoy.isoformat(), "vistas": vistas,
            "esperado": esperado, "ratio": ratio, "veredicto": texto, "emoji": emoji,
            "redes": {p["red"]: p.get("vistas", 0) for p in encontrados}}


def analizar_tanda(cli, ciclo):
    """(datos de la tanda, lista de (pieza, resultado)). resultado puede ser None."""
    datos = cargar_hipotesis(cli, ciclo)
    if not datos:
        return None, []
    posts = cargar_posts(cli)
    piezas = datos.get("piezas", [])
    fechas = {p.get("publicado") for p in piezas if p.get("publicado")}
    grupos, redes = liston(posts, fechas)
    hoy = datetime.date.today()
    return datos, [(p, evaluar(p, posts, grupos, redes, hoy)) for p in piezas]


# ---------------------------------------------------------------- informes
def informe(cli, ciclo):
    datos, filas = analizar_tanda(cli, ciclo)
    if datos is None:
        return [f"No hay hipótesis de {nombre(cli)} en {ciclo}.",
                f"Se crea con: termometro.py {cli} --nueva --ciclo {ciclo}"]
    L = [f"🌡️  {nombre(cli)} · {ciclo}"]
    if datos.get("objetivo"):
        L.append(f"    {datos['objetivo']}")
    L.append("")
    if not cargar_posts(cli):
        L.append("⚠️ No hay métricas descargadas de este cliente.")
        L.append("   Ejecuta antes: infra/metricool/fetch_metricool.py")
        L.append("")
    # Medidas primero y ordenadas por ratio: se lee como un ranking de qué funcionó.
    medidas = [(f, r) for f, r in filas if r and r.get("estado") == "medido"]
    otras = [(f, r) for f, r in filas if not (r and r.get("estado") == "medido")]
    for pieza, res in sorted(medidas, key=lambda x: x[1]["ratio"], reverse=True):
        L.append(f"{res['emoji']} {pieza.get('titulo', pieza.get('id', '?'))} "
                 f"— x{res['ratio']} ({res['vistas']} vistas vs {res['esperado']} normales)")
        L.append(f"    apuesta: {pieza.get('apuesta', '—')}")
        redes = " · ".join(f"{r} {v}" for r, v in res["redes"].items())
        L.append(f"    {redes}")
    for pieza, res in otras:
        t = pieza.get("titulo", pieza.get("id", "?"))
        if res is None:
            L.append(f"⏳ {t} — sin publicar")
        elif res["estado"] == "verde":
            L.append(f"⏳ {t} — publicada hace {res['dias']}d "
                     f"(se juzga a los {DIAS_MADUREZ})")
        elif res["estado"] == "sin_datos":
            L.append(f"⚠️ {t} — no encuentro publicación del "
                     f"{pieza.get('publicado')} en las métricas")
        else:
            L.append(f"⚠️ {t} — sin listón para comparar (faltan datos del cliente)")
    if medidas:
        L.append("")
        ratios = [r["ratio"] for _, r in medidas]
        ganan = sum(1 for x in ratios if x >= 1.2)
        L.append(f"Resumen: {len(medidas)} medidas · {ganan} por encima de lo normal · "
                 f"mediana x{round(statistics.median(ratios), 2)}")
    return L


def revisar(cli, ciclo):
    """La tanda entera en legible, para aprobarla o cambiarla.

    Se genera desde el JSON, no se guarda en ningún sitio: si hubiera un .md con las mismas
    hipótesis, en dos semanas diría otra cosa que el JSON. Fuente única.
    """
    datos = cargar_hipotesis(cli, ciclo)
    if not datos:
        return [f"No hay hipótesis de {nombre(cli)} en {ciclo}."]
    L = [f"🌡️  {nombre(cli)} · {ciclo} — {len(datos.get('piezas', []))} apuestas", ""]
    if datos.get("objetivo"):
        L += [datos["objetivo"], ""]
    if datos.get("restricciones"):
        # Las restricciones de rodaje mandan sobre las ideas: si no se leen antes, se
        # aprueban piezas imposibles de grabar.
        L.append("Con lo que hay que contar sí o sí:")
        L += [f"  · {r}" for r in datos["restricciones"]]
        L.append("")
    if datos.get("_estado"):
        L += [f"⚠️ {datos['_estado']}", ""]
    for i, p in enumerate(datos.get("piezas", []), 1):
        L.append(f"{i}. {p.get('titulo') or '(sin título)'}")
        L.append(f"   Apuesta: {p.get('apuesta') or '—'}")
        L.append(f"   Porque:  {p.get('porque') or '—'}")
        if p.get("etiquetas"):
            L.append(f"   Etiquetas: {', '.join(p['etiquetas'])}")
        if p.get("publicado"):
            L.append(f"   Publicada: {p['publicado']}")
        L.append("")
    L.append("Para cambiar algo: dile a Winy el número y qué cambias.")
    return L


def por_etiquetas(cli):
    """Qué etiqueta funciona, sumando TODAS las tandas del cliente.

    Aquí es donde el termómetro deja de ser un informe y empieza a ser memoria: una tanda
    sola no demuestra nada, pero la misma etiqueta repetida cinco meses sí.
    """
    acumulado = {}
    for _, ciclo in ciclos_con_hipotesis(cli):
        _, filas = analizar_tanda(cli, ciclo)
        for pieza, res in filas:
            if not res or res.get("estado") != "medido":
                continue
            for et in pieza.get("etiquetas") or ["(sin etiqueta)"]:
                acumulado.setdefault(et, []).append(res["ratio"])
    if not acumulado:
        return [f"Aún no hay piezas medidas de {nombre(cli)}."]
    L = [f"🌡️  {nombre(cli)} — qué funciona, por etiqueta", ""]
    orden = sorted(acumulado.items(), key=lambda kv: statistics.median(kv[1]), reverse=True)
    for et, ratios in orden:
        m = round(statistics.median(ratios), 2)
        emoji, _ = veredicto(m)
        if len(ratios) == 1:
            L.append(f"{emoji} {et}: x{m} sobre 1 pieza  (no concluye nada todavía)")
        else:
            L.append(f"{emoji} {et}: x{m} sobre {len(ratios)} piezas")
    return L


def piezas_publicadas(cli=None):
    """[(cliente, pieza)] de lo publicado en Notion (snapshot de clasificacion.py)."""
    out = []
    for ruta in sorted(glob.glob(os.path.join(PIEZAS_NOTION, "*.json"))):
        c = os.path.basename(ruta)[:-5]
        if cli and c != cli:
            continue
        try:
            with open(ruta, encoding="utf-8") as f:
                out += [(c, p) for p in json.load(f).get("piezas", [])]
        except (OSError, ValueError):
            continue
    return out


def medir_publicadas(cli=None):
    """[(cliente, pieza, resultado)] cruzando cada pieza por fecha con Metricool.

    El listón de cada pieza es la mediana del cliente SIN esa pieza (si no, se compararía
    consigo misma). Dos piezas el mismo día no se pueden separar: se descartan las dos antes
    que atribuirle a una las vistas de la otra.
    """
    hoy = datetime.date.today()
    out, posts_de = [], {}
    publicadas = piezas_publicadas(cli)
    por_fecha = {}
    for c, p in publicadas:
        por_fecha.setdefault((c, p.get("publicado")), []).append(p)
    for c, p in publicadas:
        if len(por_fecha[(c, p.get("publicado"))]) > 1:
            continue
        if c not in posts_de:
            posts_de[c] = cargar_posts(c)
        grupos, redes = liston(posts_de[c], {p.get("publicado")})
        out.append((c, p, evaluar(p, posts_de[c], grupos, redes, hoy)))
    return out


def por_campo(campo, titulo, cli=None, aviso=None):
    """Mediana del ratio (vistas / listón del cliente) agrupando piezas por `campo`.

    Es la misma cuenta para plantilla, formato, tipo de idea o autor: solo cambia la columna.
    Sin cliente cruza todos — un formato es una apuesta sobre cómo se cuenta algo, y eso
    se aprende antes cruzando clientes. Con cliente se ven sus excepciones.
    """
    acumulado, esperando, total = {}, 0, 0
    for _, pieza, res in medir_publicadas(cli):
        total += 1
        if not res or res.get("estado") != "medido":
            esperando += 1
            continue
        valor = pieza.get(campo) or f"(sin {titulo})"
        acumulado.setdefault(valor, []).append(res["ratio"])
    quien = nombre(cli) if cli else "todos los clientes"
    if not acumulado:
        return [f"Aún no hay piezas medidas con {titulo} en {quien}"
                + (f" ({esperando} publicadas esperando datos o madurez)." if esperando else ".")]
    L = [f"🌡️  {quien} — qué {titulo} funciona", ""]
    orden = sorted(acumulado.items(), key=lambda kv: statistics.median(kv[1]), reverse=True)
    for valor, ratios in orden:
        m = round(statistics.median(ratios), 2)
        emoji, _ = veredicto(m)
        if len(ratios) == 1:
            L.append(f"{emoji} {valor}: x{m} sobre 1 pieza  (no concluye nada todavía)")
        else:
            L.append(f"{emoji} {valor}: x{m} sobre {len(ratios)} piezas")
    L.append("")
    medidas = sum(len(v) for v in acumulado.values())
    L.append(f"{medidas} piezas medidas · {esperando} aún sin datos o con menos de "
             f"{DIAS_MADUREZ} días.")
    L.append(aviso or "Lo que tiene una sola pieza no decide nada: repítelo antes de creértelo.")
    return L


def por_ideas(cli=None):
    """Lo que lee Oli antes de proponer: formato + tipo de idea + autor, en un solo bloque."""
    return (por_campo("formato", "formato", cli) + [""]
            + por_campo("tipo_idea", "tipo de idea", cli) + [""]
            + por_campo("autor", "autor", cli))


def por_plantilla(cli=None):
    """Qué MECÁNICA funciona (`agentes/guiones/plantillas/`), no qué vídeo funcionó."""
    return por_campo("plantilla", "plantilla", cli,
                     aviso="Una plantilla con una sola medición no decide nada. "
                           "Las piezas anteriores al 13/08/2026 no la llevan.")


def _esperando(res):
    """¿Esta pieza todavía puede cambiar? Sin publicar o demasiado reciente para juzgarla."""
    return res is None or res.get("estado") == "verde"


def pendientes():
    """Líneas para el estado diario. Calla si no hay nada que hacer."""
    out = []
    for cli, ciclo in ciclos_con_hipotesis():
        datos, filas = analizar_tanda(cli, ciclo)
        if not datos or datos.get("cerrado"):
            continue
        medidas = [r for _, r in filas if r and r.get("estado") == "medido"]
        esperando = [r for _, r in filas if _esperando(r)]
        if not medidas:
            continue                      # tanda recién escrita: nada que contar aún
        if esperando:
            out.append(f"- {nombre(cli)} ({ciclo}): {len(medidas)} piezas medidas, "
                       f"{len(esperando)} aún sin número")
        else:
            out.append(f"- {nombre(cli)} ({ciclo}): la tanda entera ya se puede juzgar · "
                       f"`termometro.py {cli} --ciclo {ciclo} --cerrar`")
    return out


# ---------------------------------------------------------------- escritura
def cerrar(cli, ciclo):
    """Guarda los resultados dentro de hipotesis.json. Solo escribe lo ya medido."""
    datos, filas = analizar_tanda(cli, ciclo)
    if datos is None:
        return [f"No hay hipótesis de {nombre(cli)} en {ciclo}."]
    n = 0
    for pieza, res in filas:
        if res and res.get("estado") == "medido":
            pieza["resultado"] = {k: v for k, v in res.items() if k not in ("estado", "emoji")}
            n += 1
    # Se cierra cuando ya no queda nada por esperar. Una pieza que no aparece en las
    # métricas no bloquea el cierre: se queda marcada en el informe como lo que es, un
    # problema de datos, y deja de dar la lata cada día.
    datos["cerrado"] = not any(_esperando(r) for _, r in filas)
    with open(ruta_hipotesis(cli, ciclo), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    L = informe(cli, ciclo)
    L.append("")
    L.append(f"💾 Guardados {n} resultados en ciclos/{ciclo}/{cli}/hipotesis.json"
             + ("" if datos["cerrado"] else " (la tanda sigue abierta)"))
    if datos["cerrado"]:
        L.append("   Siguiente paso: escribir el aprendizaje en "
                 "memoria/aprendizajes/registro.md y sacar de ahí las ideas del mes que viene.")
    return L


def nueva(cli, ciclo, n=8):
    """Crea el esqueleto de una tanda. Los textos los escribe una persona."""
    ruta = ruta_hipotesis(cli, ciclo)
    if os.path.exists(ruta):
        return [f"Ya existe: ciclos/{ciclo}/{cli}/hipotesis.json (no lo toco)"]
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    corto = cli.split("-")[0][:2]
    datos = {
        "cliente": cli, "ciclo": ciclo, "objetivo": "",
        "piezas": [{"id": f"{corto}-{ciclo[-2:]}-{i}", "titulo": "", "apuesta": "",
                    "porque": "", "etiquetas": [], "publicado": None, "resultado": None}
                   for i in range(1, n + 1)],
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return [f"Creado ciclos/{ciclo}/{cli}/hipotesis.json con {n} piezas vacías.",
            "Rellena titulo/apuesta/porque/etiquetas. Ver ciclos/HIPOTESIS.md."]


# ---------------------------------------------------------------- cli
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    def valor(flag, defecto=None):
        if flag in sys.argv:
            i = sys.argv.index(flag) + 1
            if i < len(sys.argv) and not sys.argv[i].startswith("--"):
                return sys.argv[i]
        return defecto

    ciclo = valor("--ciclo")
    agregados = {
        "--formatos": lambda c: por_campo("formato", "formato", c),
        "--estructuras": lambda c: por_campo("formato", "formato", c),   # nombre viejo
        "--autores": lambda c: por_campo("autor", "autor", c),
        "--tipos-idea": lambda c: por_campo("tipo_idea", "tipo de idea", c),
        "--ideas": por_ideas,
    }
    for flag, fn in agregados.items():
        if flag in flags:
            print("\n".join(fn(args[0] if args else None)))
            return 0
    if not args:
        # `--plantillas` sin cliente = la comparativa global entre mecánicas.
        if "--plantillas" in flags:
            print("\n".join(por_plantilla()))
            return 0
        pend = pendientes()
        print("\n".join(pend) if pend else "No hay tandas que cerrar.")
        return 0
    cli = args[0]
    if "--plantillas" in flags:
        print("\n".join(por_plantilla(cli)))
        return 0
    if "--etiquetas" in flags:
        print("\n".join(por_etiquetas(cli)))
        return 0
    if "--revisar" in flags and not ciclo:
        disponibles = ciclos_con_hipotesis(cli)
        ciclo = disponibles[0][1] if disponibles else None
    if "--nueva" in flags:
        # Una tanda nueva siempre es de un mes concreto: no se adivina.
        if not ciclo:
            print("uso: termometro.py <cliente> --nueva --ciclo YYYY-MM [--piezas N]")
            return 2
        print("\n".join(nueva(cli, ciclo, int(valor("--piezas", "8")))))
        return 0
    if not ciclo:
        # Sin --ciclo, la más reciente que tenga hipótesis.
        disponibles = ciclos_con_hipotesis(cli)
        if not disponibles:
            print(f"No hay ninguna tanda de {nombre(cli)}. "
                  f"Créala con: termometro.py {cli} --nueva --ciclo YYYY-MM")
            return 1
        ciclo = disponibles[0][1]
    if "--revisar" in flags:
        print("\n".join(revisar(cli, ciclo)))
        return 0
    print("\n".join(cerrar(cli, ciclo) if "--cerrar" in flags else informe(cli, ciclo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
