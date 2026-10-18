#!/usr/bin/env python3
"""Recolector de estado del sistema — Python puro, 0 tokens.

Reúne DE UNA VEZ todo lo que Winy (responder) y el check-in de Winston necesitan saber, y
escribe un bloque compacto en `infra/estado/estado.txt`. Sustituye a la exploración con
Glob/Read que antes hacía el modelo (que era lo que multiplicaba turnos y contexto): el
modelo pasa de *buscar* la información a solo *redactarla*.

Recoge:
  - Ciclos activos      -> ciclos/*/*/manifest.json (etapa, estado, gates pendientes)
  - Cobertura           -> reutiliza infra/metricool/chequeo_cobertura.py (cacheada)
  - Notas de Gerard     -> ../notas/*.md, SOLO las líneas "- [ ]" sin marcar
  - Aprendizajes        -> memoria/aprendizajes/registro.md, solo si cambió en 7 días

Uso:
  estado.py                 -> imprime el bloque y lo guarda en estado.txt
  estado.py --refrescar     -> además reconsulta en vivo la cobertura y la Bandeja (~10s)
"""
import datetime
import glob
import json
import os
import re
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
VAULT = os.path.dirname(HUB)                      # /Users/gerardruizmiro/rmagency
AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "estado.txt")
COBERTURA_CACHE = os.path.join(HUB, "memoria/metricas/_cobertura.md")
BANDEJA_CACHE = os.path.join(HUB, "infra/notion/_bandeja.txt")
# Repo del análisis mensual (fuente canónica del Analista; ver config/rutas.md → ANALISIS).
# Se movió a ~/rmagency/proyectos/ con la migración; en ~/Documents ya no está (13/08/2026).
ANALISIS_REGISTRO = os.path.join(VAULT, "proyectos/Analisis mensual/registro-analisis.json")

MAX_NOTAS = 12          # tope de tareas sin marcar que se inyectan
MAX_APRENDIZAJES = 6    # tope de líneas de aprendizajes
DIAS_APRENDIZAJES = 7   # solo si el registro se tocó en los últimos N días
CACHE_HORAS = 24        # a partir de aquí la cobertura se marca como vieja
ANALISIS_VENTANA_DIAS = 20  # solo avisa del análisis del 1 al N (ventana de llegada de brutos)

# Meses en catalán (el registro del Analista guarda "mes" así, p.ej. "Juny 2026").
MESOS_CAT = ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
             "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]

# Etapas de un manifest, en orden de flujo, con su nombre "humano" (sin jerga para Winy).
ETAPAS = [
    ("estrategia", "estrategia"), ("grabacion", "grabación"), ("edicion", "edición"),
    ("copies", "copies"), ("qa", "QA"), ("distribucion", "distribución"), ("cierre", "cierre"),
]
NOMBRES = {"jesus-mora": "Jesús Mora", "xavi-colomina": "Xavi", "golossa": "Golossa",
           "midtown": "Midtown", "msm": "MSM", "newmos": "Newmos"}


def nombre(slug):
    return NOMBRES.get(slug, slug)


# ---------------------------------------------------------------- ciclos
def leer_ciclos():
    """Una línea por ciclo activo: en qué etapa está y qué gates esperan a Gerard."""
    out = []
    for ruta in sorted(glob.glob(os.path.join(HUB, "ciclos/*/*/manifest.json"))):
        try:
            with open(ruta, encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        cli = nombre(m.get("cliente", os.path.basename(os.path.dirname(ruta))))
        ciclo = m.get("ciclo", "")
        partes, gates = [], []
        for clave, humano in ETAPAS:
            bloque = m.get(clave)
            if not isinstance(bloque, dict):
                continue
            est = bloque.get("estado")
            if est and est != "pendiente":
                partes.append(f"{humano}={est}")
            # Gate = etapa lista/entregable pero sin el OK de Gerard
            if bloque.get("aprobado_gerard") is False and est in ("listo", "adelantado"):
                gates.append(humano)
        desp = m.get("despacho") or {}
        sig = desp.get("siguiente_agente")
        linea = f"- {cli} ({ciclo}): " + (", ".join(partes) if partes else "sin arrancar")
        if sig:
            linea += f" · toca a: {sig}"
        if gates:
            linea += f" · 🔔 espera tu OK en: {', '.join(gates)}"
        out.append(linea)
        # Notas que Gerard dejó dentro del manifest (contexto que el modelo no debe ir a buscar)
        for campo in ("nota", "nota_prueba"):
            for clave, _ in ETAPAS:
                bloque = m.get(clave)
                if isinstance(bloque, dict) and bloque.get(campo):
                    out.append(f"    · {bloque[campo][:200]}")
        if desp.get("nota"):
            out.append(f"    · {desp['nota'][:200]}")
    return out or ["- (no hay ciclos activos)"]


# ---------------------------------------------------------------- cobertura
def leer_cobertura(refrescar=False):
    """Informe de cobertura. Por defecto usa la caché (rápido); --refrescar consulta la API."""
    if refrescar:
        sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
        try:
            import chequeo_cobertura
            msg = chequeo_cobertura.construir_informe()
            with open(COBERTURA_CACHE, "w", encoding="utf-8") as f:
                f.write(f"# Cobertura de programación · "
                        f"{datetime.datetime.now():%Y-%m-%d %H:%M}\n\n{msg}\n")
            return msg
        except Exception as e:
            return f"⚠️ No pude consultar la cobertura ahora mismo ({e})."
    try:
        edad_h = (datetime.datetime.now().timestamp()
                  - os.path.getmtime(COBERTURA_CACHE)) / 3600
        with open(COBERTURA_CACHE, encoding="utf-8") as f:
            cuerpo = f.read().split("\n", 2)[-1].strip()
        if edad_h > CACHE_HORAS:
            cuerpo += f"\n(dato de hace {int(edad_h)}h — puede haber cambiado)"
        return cuerpo
    except FileNotFoundError:
        return "(cobertura aún no calculada)"


# ---------------------------------------------------------------- notas de Obsidian
# Metadata OPCIONAL de un recordatorio, al final entre paréntesis. Ejemplo:
#   - [ ] Llamar a Golossa por el reel (📅 2026-07-30 · ⚡alta · #golossa)
# Todo es opcional y retrocompatible: una nota sin metadata funciona igual que siempre.
_META_FECHA = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")


def _fecha_nota(texto):
    """Fecha de vencimiento (date) si la nota trae '📅 YYYY-MM-DD', si no None."""
    m = _META_FECHA.search(texto)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def leer_notas():
    """Tareas SIN marcar ('- [ ]') de las notas de Gerard, ordenadas por vencimiento.

    Las que traen '📅 YYYY-MM-DD' van primero, de la más urgente a la más lejana, y se
    marcan con ⚠️ si ya vencieron. Las que no traen fecha van después, en orden de aparición.
    Retrocompatible: una nota sin metadata sale igual que antes.
    """
    hoy = datetime.date.today()
    items = []  # (clave_orden, texto_render)
    for ruta in sorted(glob.glob(os.path.join(VAULT, "notas/*.md"))):
        try:
            with open(ruta, encoding="utf-8") as f:
                lineas = f.read().splitlines()
        except Exception:
            continue
        dentro_de_comentario = False
        for ln in lineas:
            s = ln.strip()
            # Ignorar los ejemplos comentados de la plantilla
            if "<!--" in s:
                dentro_de_comentario = True
            if dentro_de_comentario:
                if "-->" in s:
                    dentro_de_comentario = False
                continue
            if s.startswith("- [ ]"):
                cuerpo = s[5:].strip()
                fecha = _fecha_nota(cuerpo)
                if fecha is not None:
                    venc = "⚠️ " if fecha < hoy else ""
                    items.append(((0, fecha), f"- {venc}{cuerpo[:160]}"))
                else:
                    items.append(((1, datetime.date.max), f"- {cuerpo[:160]}"))
    items.sort(key=lambda x: x[0])
    return [t for _, t in items[:MAX_NOTAS]]


# ---------------------------------------------------------------- aprendizajes
def leer_aprendizajes():
    """Títulos de los aprendizajes recientes, solo si el registro se tocó hace poco."""
    ruta = os.path.join(HUB, "memoria/aprendizajes/registro.md")
    try:
        dias = (datetime.datetime.now().timestamp() - os.path.getmtime(ruta)) / 86400
    except OSError:
        return []
    if dias > DIAS_APRENDIZAJES:
        return []
    try:
        with open(ruta, encoding="utf-8") as f:
            lineas = f.read().splitlines()
    except Exception:
        return []
    # Cada aprendizaje empieza con "### fecha · cliente · tipo"; nos quedamos con el "Qué".
    titulos = []
    for i, ln in enumerate(lineas):
        if ln.startswith("### "):
            cab = ln[4:].strip()
            que = ""
            for sig in lineas[i + 1:i + 4]:
                if sig.startswith("**Qué:**"):
                    que = sig[8:].strip()
                    break
            titulos.append(f"- {cab}: {que[:140]}")
    return titulos[-MAX_APRENDIZAJES:]


# ---------------------------------------------------------------- análisis mensual
def leer_analisis_pendiente():
    """Análisis mensual de cierre que falta por hacer — el 'disparador' del Analista.

    Sin credenciales ni tokens: cruza el calendario (el análisis de un mes se hace al
    principio del mes siguiente → objetivo = mes anterior) con el registro de ANALISIS.
    Solo avisa dentro de la ventana en que llegan los brutos de Metricool (días 1..N) y
    solo si queda algún cliente pendiente; fuera de esa ventana calla (no dar la lata).
    """
    hoy = datetime.date.today()
    if hoy.day > ANALISIS_VENTANA_DIAS:
        return []
    y, m = (hoy.year, hoy.month - 1) if hoy.month > 1 else (hoy.year - 1, 12)
    objetivo = f"{MESOS_CAT[m - 1]} {y}"
    try:
        with open(ANALISIS_REGISTRO, encoding="utf-8") as f:
            reg = json.load(f)
    except Exception:
        return []
    clientes = reg.get("clientes") or []
    if not clientes:
        return []
    hechos = {a.get("cliente") for a in reg.get("analisis", [])
              if a.get("mes") == objetivo and a.get("estado") == "completado"}
    faltan = [c for c in clientes if c not in hechos]
    if not faltan:
        return []
    return [
        f"- Mes: {objetivo} · faltan por hacer: {', '.join(faltan)} (de {len(clientes)})",
        "- Acción: arrancar el Analista en sesión (los brutos de Metricool ya deberían "
        "estar en el correo)",
    ]


def leer_ciclo():
    """Qué fase del reloj le toca a cada cliente esta semana (config/ciclo-mensual.json).

    Best-effort: si el reloj falla, el resto del estado sigue saliendo igual.
    """
    try:
        sys.path.insert(0, AQUI)
        import ciclo
        return ciclo.informe()
    except Exception:  # noqa: BLE001
        return []


def refrescar_bandeja():
    """Recalcula la caché de la Bandeja ANTES de leerla.

    Por qué: el check-in corre a las 00:30 y `bandeja.py` se ejecuta dentro de `noche.sh` a
    las 00:45, así que Winy leía siempre el recuento de la noche anterior. El 13/08/2026 el
    check-in cantaba "14 ideas / 5 con cliente" cuando ya eran 19 y 10. Refrescando aquí, el
    dato es de hace segundos y `noche.sh` puede seguir llamando a bandeja.py sin molestar
    (escriben lo mismo). Best-effort: si Notion no contesta, se cae a la caché de siempre.
    """
    try:
        sys.path.insert(0, os.path.join(HUB, "infra/notion"))
        import bandeja
        lineas = bandeja.resumen()
        with open(BANDEJA_CACHE, "w", encoding="utf-8") as f:
            f.write(f"# {datetime.datetime.now():%Y-%m-%d %H:%M}\n" + "\n".join(lineas) + "\n")
    except Exception:  # noqa: BLE001
        pass


def leer_bandeja():
    """Ideas atascadas en la Bandeja de Notion (caché que escribe `infra/notion/bandeja.py`).

    Es el único gate humano de la fábrica: si nadie aprueba, `distribuir.py` dice "nada que
    hacer" y todo parece bien. Sin este aviso el atasco es invisible.
    """
    try:
        edad_h = (datetime.datetime.now().timestamp() - os.path.getmtime(BANDEJA_CACHE)) / 3600
        with open(BANDEJA_CACHE, encoding="utf-8") as f:
            cuerpo = f.read().split("\n", 1)[-1].strip()
    except OSError:
        return []
    if not cuerpo:
        return []
    if edad_h > CACHE_HORAS * 2:
        cuerpo += f"\n(dato de hace {int(edad_h / 24)}d)"
    return cuerpo.splitlines()


CREADORES_PEND = os.path.join(HUB, "memoria/analisis/_creadores_pendientes.txt")


def leer_creadores_pendientes():
    """Referencias de Instagram sin @creador (caché de infra/olivia/referencias.py, 08/10/2026).
    Instagram no se consulta solo: el @ lo pone Gerard, y esto se lo recuerda."""
    try:
        with open(CREADORES_PEND, encoding="utf-8") as f:
            return [l for l in f.read().splitlines()[1:] if l.strip()]
    except OSError:
        return []


def leer_termometro():
    """Tandas de hipótesis con piezas ya medibles (ver `ciclos/HIPOTESIS.md`).

    Calla mientras no haya números: una tanda recién escrita no sale, y una ya cerrada
    tampoco. Best-effort, como el reloj.
    """
    try:
        sys.path.insert(0, AQUI)
        import termometro
        return termometro.pendientes()
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------- montaje
def construir(refrescar=False):
    hoy = datetime.date.today()
    dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    L = [f"FECHA: {dias_es[hoy.weekday()]} {hoy:%d/%m/%Y}", ""]
    rel = leer_ciclo()
    if rel:
        L.append("EL RELOJ — QUÉ TOCA ESTA SEMANA:")
        L += rel
        L.append("")
    L.append("CICLOS ACTIVOS:")
    L += leer_ciclos()
    L.append("")
    L.append("COBERTURA DE PROGRAMACIÓN:")
    L.append(leer_cobertura(refrescar))
    L.append("")
    if refrescar:
        refrescar_bandeja()
    ban = leer_bandeja()
    if ban:
        L.append("BANDEJA DE IDEAS (esperan tu OK):")
        L += ban
        L.append("")
    cre = leer_creadores_pendientes()
    if cre:
        L.append("CREADORES DE REFERENCIA (falta el @):")
        L += cre
        L.append("")
    term = leer_termometro()
    if term:
        L.append("TERMÓMETRO — HIPÓTESIS CON NÚMEROS:")
        L += term
        L.append("")
    ana = leer_analisis_pendiente()
    if ana:
        L.append("ANÁLISIS MENSUAL PENDIENTE:")
        L += ana
        L.append("")
    notas = leer_notas()
    L.append("NOTAS DE GERARD SIN HACER:")
    L += notas or ["- (ninguna)"]
    L.append("")
    apr = leer_aprendizajes()
    if apr:
        L.append("APRENDIZAJES RECIENTES:")
        L += apr
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    bloque = construir("--refrescar" in sys.argv)
    with open(DEST, "w", encoding="utf-8") as f:
        f.write(bloque)
    sys.stdout.write(bloque)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
