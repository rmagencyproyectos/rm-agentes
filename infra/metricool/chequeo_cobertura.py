#!/usr/bin/env python3
"""Chequeo de cobertura de programación (para que Winy avise a Gerard).

Verifica, por cliente, que los slots de publicación obligatorios de los próximos días
estén **programados de verdad**: en su día, a las **15:00**, en **todas las redes del
cliente** (`redes` en `config/metricool-marcas.json`, por defecto Instagram + TikTok) y
**NO en borrador**.

Los días, las **pausas** y las **excepciones temporales** salen de `config/publicacion.json`,
que es la **fuente única**. No hay reglas escritas a mano en este fichero: si hay que cambiar
un día, se cambia el JSON y ya. `config/calendario-publicacion.md` solo lo explica.

Redacta un mensaje SUPER COMPACTO en voz de Winy y, con --send, lo manda por WhatsApp
(notify.sh).

Uso:  chequeo_cobertura.py [--send] [--dias N]
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
DIAS_VENTANA = 12
DIAS_ES = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

CORTO = {"jesus-mora": "Jesús Mora", "xavi-colomina": "Xavi", "golossa": "Golossa",
         "midtown": "Midtown", "msm": "MSM", "newmos": "Newmos"}


# --- Calendario: se carga de config/publicacion.json (fuente única) -------------------

def _cargar_publicacion():
    with open(os.path.join(HUB, "config/publicacion.json"), encoding="utf-8") as f:
        return json.load(f)


_PUB = _cargar_publicacion()

# weekday() -> 0=Lun .. 6=Dom. Las claves del JSON son texto; aquí pasan a int.
REGLAS = {cli: {"dias": {int(k): v for k, v in dias.items()}}
          for cli, dias in _PUB["dias"].items()}
PAUSAS = _PUB.get("pausas", {})
EXCEPCIONES = _PUB.get("excepciones", [])


def _dentro(fecha, desde, hasta):
    """¿`fecha` cae en el rango? `hasta` a None = abierto (sin fecha de vuelta)."""
    if desde and fecha < datetime.date.fromisoformat(desde):
        return False
    if hasta and fecha > datetime.date.fromisoformat(hasta):
        return False
    return True


def pausa_de(cli, fecha):
    """Devuelve la pausa activa del cliente en esa fecha, o None."""
    p = PAUSAS.get(cli)
    if p and _dentro(fecha, p.get("desde"), p.get("hasta")):
        return p
    return None


def dias_para(cli, fecha):
    """Días de publicación del cliente EN ESA FECHA: {weekday: tipo}.

    Aplica, por orden: pausa (devuelve {}), excepción temporal, y si no, la regla base.
    """
    if pausa_de(cli, fecha):
        return {}
    for e in EXCEPCIONES:
        if e.get("cliente") == cli and _dentro(fecha, e.get("desde"), e.get("hasta")):
            return {int(k): v for k, v in e["dias"].items()}
    return REGLAS.get(cli, REGLAS["_default"])["dias"]


def redes_de(cli):
    """Redes que DEBE llevar un post de este cliente para contar como cubierto.
    Fuente única: `redes` del cliente en config/metricool-marcas.json (o `_redes_default`).
    Se sacó de aquí el 21/08/2026, al añadir YouTube Shorts a Xavi."""
    try:
        with open(os.path.join(HUB, "config/metricool-marcas.json"), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"instagram", "tiktok"}
    for grupo in ("roster_v1", "fuera_de_roster_v1"):
        entrada = (data.get(grupo) or {}).get(cli)
        if isinstance(entrada, dict) and entrada.get("redes"):
            return set(entrada["redes"])
    return set(data.get("_redes_default") or ["instagram", "tiktok"])


def load_env():
    env = {}
    with open(os.path.join(HUB, "infra/.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


def api_get(path, tok):
    r = urllib.request.Request("https://app.metricool.com/api" + path,
                               headers={"X-Mc-Auth": tok, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_programados(blog, uid, tok, hoy, fin):
    q = f"start={hoy:%Y-%m-%d}T00:00:00&end={fin:%Y-%m-%d}T23:59:59&blogId={blog}&userId={uid}"
    d = api_get("/v2/scheduler/posts?" + q, tok)
    return d.get("data", d) if isinstance(d, dict) else d


def analizar(cli, posts, hoy, fin):
    # Indexar posts programados por fecha
    por_fecha = {}
    for p in posts:
        dt = (p.get("publicationDate") or {}).get("dateTime", "")
        try:
            d = datetime.datetime.fromisoformat(dt)
        except Exception:
            continue
        nets = {pr.get("network", "") for pr in (p.get("providers") or [])}
        por_fecha.setdefault(d.date(), []).append(
            {"hora": d.strftime("%H:%M"), "draft": bool(p.get("draft")), "nets": nets})
    # Recorrer los slots obligatorios en la ventana
    cubierto_hasta = None
    fallo = None
    dia = hoy
    while dia <= fin:
        # Los días se piden por fecha: así se respetan pausas y excepciones temporales.
        tipo = dias_para(cli, dia).get(dia.weekday())
        if tipo:
            posts_dia = por_fecha.get(dia, [])
            ok = a_las_15_ok = falta_red = hay_draft = False
            for pd in posts_dia:
                if pd["draft"]:
                    hay_draft = True
                    continue
                if pd["hora"] == "15:00":
                    if tipo == "corta" or (redes_de(cli) <= pd["nets"]):
                        ok = True
                    else:
                        a_las_15_ok = True
                        falta_red = True
            if ok:
                cubierto_hasta = dia
            else:
                if falta_red:
                    motivo = "falta IG o TikTok"
                elif hay_draft:
                    motivo = "en borrador"
                elif posts_dia:
                    motivo = "hora mal (no 15:00)"
                else:
                    motivo = "sin programar"
                fallo = (dia, tipo, motivo)
                break
        dia += datetime.timedelta(days=1)
    return cubierto_hasta, fallo


def stock_notion(slug):
    """Sufijo con el stock del cliente en Notion: 📦 editadas sin programar · 🎬 a grabar ·
    ✍️ aprobadas sin guion. Es lo que contesta "hasta cuándo tenemos material". Best-effort:
    si Notion no está accesible o falta el token, devuelve "" y la cobertura sigue igual."""
    try:
        sys.path.insert(0, os.path.join(HUB, "infra/notion"))
        import notion_api as na
        tok = na.token()
        cli = na.load_config()["clientes"].get(slug)
        if not cli:
            return ""
        db = cli["database_id"]

        def n(filtro):
            return len(na.query(db, tok, filtro))

        editadas = n({"and": [{"property": "Producción", "select": {"equals": "Editado"}},
                              {"property": "Publicación", "date": {"is_empty": True}}]})
        agrabar = n({"and": [{"property": "Resolución", "select": {"equals": "Aprobada"}},
                             {"property": "Guion", "select": {"equals": "Listo"}},
                             {"property": "Producción", "select": {"equals": "Pendiente de grabar"}}]})
        singuion = n({"and": [{"property": "Resolución", "select": {"equals": "Aprobada"}},
                              {"property": "Guion", "select": {"equals": "Sin empezar"}}]})
        partes = []
        if editadas:
            partes.append(f"📦{editadas}")
        if agrabar:
            partes.append(f"🎬{agrabar}")
        if singuion:
            partes.append(f"✍️{singuion}")
        return (" · " + " ".join(partes)) if partes else ""
    except Exception:  # noqa: BLE001
        return ""


def icono(fallo, cubierto):
    if fallo is None:
        return "✅"
    dia, tipo, motivo = fallo
    return "🔴" if motivo == "sin programar" else "🟡"


def linea(label, cubierto, fallo):
    if fallo is None:
        h = f"ok hasta {DIAS_ES[cubierto.weekday()]} {cubierto:%d/%m}" if cubierto else "ok"
        return f"✅ {label}: {h}"
    dia, tipo, motivo = fallo
    corta = " (corta)" if tipo == "corta" else ""
    return f"{icono(fallo, cubierto)} {label}: {DIAS_ES[dia.weekday()]} {dia:%d/%m}{corta} {motivo}"


def construir_informe(dias=DIAS_VENTANA):
    """Consulta Metricool y devuelve el mensaje de cobertura ya redactado.

    Lo usan main() y `infra/estado/estado.py` (para no duplicar ni la lógica ni las REGLAS).
    Lanza RuntimeError si faltan credenciales.
    """
    env = load_env()
    tok, uid = env.get("METRICOOL_API_TOKEN"), env.get("METRICOOL_USER_ID")
    if not tok or not uid:
        raise RuntimeError("Faltan credenciales Metricool")
    marcas = json.load(open(os.path.join(HUB, "config/metricool-marcas.json")))["roster_v1"]
    hoy = datetime.date.today()
    fin = hoy + datetime.timedelta(days=dias)
    resultados = []
    for cli, info in marcas.items():
        # Pausado toda la ventana: se dice y no se consulta a la API.
        if pausa_de(cli, hoy) and pausa_de(cli, fin):
            hasta = pausa_de(cli, hoy).get("hasta")
            cuando = (f" hasta {datetime.date.fromisoformat(hasta):%d/%m}"
                      if hasta else " (sin fecha de vuelta)")
            resultados.append((2, f"⏸ {CORTO.get(cli, info['label'])}: en pausa{cuando}"))
            continue
        try:
            posts = get_programados(info["brand_id"], uid, tok, hoy, fin)
        except Exception as e:
            resultados.append((3, f"⚠️ {info['label']}: no pude consultar ({e})"))
            continue
        cubierto, fallo = analizar(cli, posts, hoy, fin)
        rank = 0 if (fallo and fallo[2] == "sin programar") else (1 if fallo else 2)
        texto = linea(CORTO.get(cli, info["label"]), cubierto, fallo) + stock_notion(cli)
        resultados.append((rank, texto))
    resultados.sort(key=lambda x: x[0])
    problemas = [t for r, t in resultados if r < 2]
    cuerpo = "\n".join(t for _, t in resultados)
    if problemas:
        return f"📅 *Cobertura* — {len(problemas)} a revisar:\n\n{cuerpo}"
    return f"📅 *Cobertura* — todo cubierto ✅\n\n{cuerpo}"


def main():
    send = "--send" in sys.argv
    dias = DIAS_VENTANA
    if "--dias" in sys.argv:
        try:
            dias = int(sys.argv[sys.argv.index("--dias") + 1])
        except (IndexError, ValueError):
            print("uso: chequeo_cobertura.py [--send] [--dias N]")
            return 2
    try:
        msg = construir_informe(dias)
    except RuntimeError as e:
        print(e)
        return 2
    print(msg)
    with open(os.path.join(HUB, "memoria/metricas/_cobertura.md"), "w", encoding="utf-8") as f:
        f.write(f"# Cobertura de programación · {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n{msg}\n")
    if send:
        subprocess.run([os.path.join(HUB, "infra/notifier/notify.sh"), msg, "COBERTURA", "normal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
