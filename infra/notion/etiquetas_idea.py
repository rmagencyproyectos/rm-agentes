#!/usr/bin/env python3
"""Las etiquetas de la idea: `Tipo de idea`, `Formato` y `Autor`. Fuente única + migración.

Pedido por Gerard el 22/09/2026: cada idea tiene que llevar DE QUÉ TIPO es y en qué FORMATO
se cuenta (ranking, lista, top 10, comparación, tips…), para que el termómetro diga qué
funciona con cada cliente y Oli proponga ideas con ese dato delante. Y QUIÉN la propuso
(Gerard, Oli…), para no perder las de Oli entre las demás y poder comparar.

⚠️ "Formato" es el formato DEL CONTENIDO (decisión de Gerard, 22/09/2026). Lo que antes se
llamaba Formato (Reel/Carrusel/Story) ahora es `Soporte`. Durante unas horas esta etiqueta
se llamó "Estructura": si aparece en algún sitio viejo, es esto mismo.

No confundir con las capas que ya había (ver `agentes/guiones/plantillas/README.md`):
  Tipo          Viral/Marca           el OBJETIVO
  Plantilla     demostracion, …       la MECÁNICA con la que Coco escribe el guion
  Soporte       Reel/Carrusel/Story   la PIEZA que se publica
  Tipo de idea  (esto)                de qué va la idea
  Formato       (esto)                la forma del contenido: tips, top, comparación…
  Autor         (esto)                quién propuso la idea

**Las opciones viven en Notion, no aquí.** Esto solo siembra las iniciales. Cuando Gerard
añade una opción nueva a mano en Notion, `opciones()` la lee en vivo y Coco ya la puede usar:
no hay una segunda lista que mantener. Coco también puede proponer una nueva si ninguna
encaja (se avisa por WhatsApp para que no crezca a escondidas).

Uso:  etiquetas_idea.py [--dry-run]     siembra las opciones que falten (idempotente)
      (para LIMPIAR y unificar listas en todas las bases: `etiquetas_sincronizar.py`)
      etiquetas_idea.py --renombrar     migración del 22/09: Formato→Soporte y Estructura→Formato
                                        (solo después de desplegar la app Calendario Edición,
                                        que lee "Soporte"; si no, escribiría Reel en Formato)
      etiquetas_idea.py --ver           enseña las opciones actuales de cada base
Salida: 0 ok · 2 falta token · 1 error
"""
import sys
import unicodedata

import notion_api as na

PROP_TIPO = "Tipo de idea"
PROP_FORMATO = "Formato"
PROP_AUTOR = "Autor"
PROP_SOPORTE = "Soporte"   # Reel/Carrusel/Story (antes "Formato")
SOPORTES = {"Reel", "TikTok", "Story", "Carrusel", "Otro"}

# Semilla. ⚠️ LISTAS CERRADAS: la fuente única es `agentes/guiones/ETIQUETAS.md` (reordenadas el
# 02/10/2026 porque las columnas se solapaban). Para añadir una opción: primero al .md con su
# definición, luego aquí, y se aplica con `etiquetas_sincronizar.py`. Si alguien añade una
# opción a mano en Notion sin pasar por el .md, el sincronizador la borra.
SEMILLA = {
    PROP_AUTOR: [
        ("Gerard", "blue"), ("Oli", "purple"), ("Andrea", "green"), ("Cliente", "orange"),
    ],
    # Formato = la FORMA de la pieza (no la mecánica del guion, que es Plantilla).
    PROP_FORMATO: [
        ("Lista / Top", "blue"), ("Tips", "yellow"), ("Comparación", "orange"),
        ("Paso a paso", "green"), ("Proceso", "brown"), ("Explicación", "gray"),
        ("Reto al espectador", "purple"), ("A pie de calle", "pink"), ("Trend", "red"),
        ("Producto en primer plano", "default"),
    ],
    # Tipo de idea = DE QUÉ VA la pieza.
    PROP_TIPO: [
        ("Producto", "green"), ("Oficio", "blue"), ("Día de trabajo", "brown"),
        ("Cliente", "orange"), ("Local y zona", "gray"), ("Opinión", "red"),
        ("Humor", "yellow"), ("Interactiva", "purple"),
    ],
}


_REALES = {}


def nombres_reales(db, tok):
    """{"Soporte": nombre real, "Formato": nombre real} de esta base, migrada o no.

    Compatibilidad para el hueco entre desplegar el código y renombrar en Notion
    (`--renombrar`). Sin migrar, lo que el código llama Soporte sigue llamándose "Formato" y el
    formato del contenido sigue llamándose "Estructura". Así ningún script escribe "Tips" en la
    columna de Reel/Carrusel, pase lo que pase con el orden. Una vez migradas todas las bases,
    esto devuelve siempre los nombres nuevos y no molesta.
    """
    if db not in _REALES:
        try:
            props = na._request("GET", f"/databases/{db}", tok).get("properties", {})
        except RuntimeError:
            props = {PROP_SOPORTE: True}      # sin red: se asume migrada (el caso normal)
        if PROP_SOPORTE in props:
            _REALES[db] = {PROP_SOPORTE: PROP_SOPORTE, PROP_FORMATO: PROP_FORMATO}
        else:
            _REALES[db] = {PROP_SOPORTE: "Formato", PROP_FORMATO: "Estructura"}
    return _REALES[db]


def traducir(props, db, tok):
    """Renombra las claves Soporte/Formato de un dict de propiedades a las reales de la base."""
    reales = nombres_reales(db, tok)
    if reales[PROP_SOPORTE] == PROP_SOPORTE:
        return props
    # Se construye de cero para que el Formato nuevo no pise al Soporte traducido.
    return {reales.get(k, k): v for k, v in props.items()}


def leer(pagina_props, nombre, db, tok):
    """Lee la propiedad `nombre` (Soporte/Formato nuevos) con el nombre real de la base."""
    return na.plain(pagina_props.get(nombres_reales(db, tok).get(nombre, nombre)))


def normalizar(s):
    """'Comparación ' == 'comparacion': para no crear duplicados por una tilde o mayúscula."""
    s = unicodedata.normalize("NFKD", (s or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def bases(cfg):
    """(etiqueta, database_id) de la Bandeja + cada base de cliente activa."""
    yield "Bandeja", cfg["bandeja"]["database_id"]
    for slug, cli in cfg["clientes"].items():
        yield cli["label"], cli["database_id"]


def opciones(database_id, tok):
    """{prop: [nombres]} leído en vivo del esquema de la base."""
    r = na._request("GET", f"/databases/{database_id}", tok)
    reales = nombres_reales(database_id, tok)
    out = {}
    for prop in (PROP_TIPO, PROP_FORMATO, PROP_AUTOR):
        p = r.get("properties", {}).get(reales.get(prop, prop))
        out[prop] = [o["name"] for o in p["select"]["options"]] if p and p.get("select") else []
    return out


def casar(valor, existentes):
    """(nombre_canónico, es_nuevo). Casa con una opción existente ignorando tildes/mayúsculas."""
    v = (valor or "").strip()
    if not v:
        return "", False
    for e in existentes:
        if normalizar(e) == normalizar(v):
            return e, False
    return v[:60], True


def renombrar(db, tok, dry):
    """Formato (Reel/Carrusel) -> Soporte, y Estructura -> Formato. Por id, en dos pasos.

    Dos PATCH separados y en este orden: si se hiciera al revés, habría un momento con dos
    propiedades llamadas "Formato". Idempotente: si ya está hecho, no toca nada.
    """
    props = na._request("GET", f"/databases/{db}", tok)["properties"]
    hechos = []
    if PROP_SOPORTE not in props and "Formato" in props:
        viejo = props["Formato"]
        ops = {o["name"] for o in viejo.get("select", {}).get("options", [])}
        # Solo es el viejo si sus opciones son de soporte; si no, es que ya es el de contenido.
        if ops & SOPORTES:
            hechos.append(("Formato", PROP_SOPORTE, viejo["id"]))
    if "Estructura" in props:
        hechos.append(("Estructura", PROP_FORMATO, props["Estructura"]["id"]))
    for antes, despues, pid in hechos:
        if not dry:
            na._request("PATCH", f"/databases/{db}", tok,
                        {"properties": {pid: {"name": despues}}})
    return [f"{a} → {d}" for a, d, _ in hechos]


def main():
    dry = "--dry-run" in sys.argv
    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    cfg = na.load_config()
    fallos = 0
    for label, db in bases(cfg):
        try:
            if "--renombrar" in sys.argv:
                cambios = renombrar(db, tok, dry)
                if cambios:
                    print(f"{'(dry-run) ' if dry else '✓ '}{label}: {' · '.join(cambios)}")
            esquema = na._request("GET", f"/databases/{db}", tok)["properties"]
            actuales = opciones(db, tok)
        except RuntimeError as e:
            sys.stderr.write(f"✗ {label}: {e}\n")
            fallos += 1
            continue
        if "--ver" in sys.argv:
            print(f"{label}:")
            for prop, ops in actuales.items():
                print(f"  {prop}: {', '.join(ops) or '(no existe)'}")
            continue
        # Seguro: sin migrar, "Formato" sigue siendo Reel/Carrusel y sembrarlo lo mezclaría.
        # Las demás (Autor, Tipo de idea) no chocan con nada y se siembran igual.
        sin_migrar = PROP_SOPORTE not in esquema
        if sin_migrar:
            print(f"⏸ {label}: Formato sin migrar (aún es Reel/Carrusel); lo demás sí. "
                  f"Corre con --renombrar.")
        # Se añaden las de la semilla que falten y se CONSERVAN las que Gerard ya haya creado.
        props = {}
        for prop, semilla in SEMILLA.items():
            if sin_migrar and prop == PROP_FORMATO:
                continue
            ya = {normalizar(n) for n in actuales[prop]}
            ops = [{"name": n} for n in actuales[prop]]
            ops += [{"name": n, "color": c} for n, c in semilla if normalizar(n) not in ya]
            props[prop] = {"select": {"options": ops}}
        if dry:
            print(f"(dry-run) {label}: siembra " + " · ".join(
                f"{p} → {', '.join(o['name'] for o in v['select']['options'])}"
                for p, v in props.items()))
            continue
        try:
            na._request("PATCH", f"/databases/{db}", tok, {"properties": props})
            print(f"✓ {label}")
        except RuntimeError as e:
            sys.stderr.write(f"✗ {label}: {e}\n")
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
