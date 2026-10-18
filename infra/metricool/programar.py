#!/usr/bin/env python3
"""Sube a Metricool la programación preparada en metricool.json — SOLO con el OK de Gerard.

Flujo (respeta el Gate 3: nada se programa sin que Gerard apriete):
  1) `calendario.py` deja `metricool.json` con los posts (fecha, 15:00, IG+TikTok, brand_id).
  2) Winy le enseña a Gerard la lista y le pregunta si le da al OK.
  3) Con el OK, se ejecuta este script:
       - sin --confirmar  -> PREVIEW: valida y enseña qué se programaría. No toca Metricool.
       - con --confirmar  -> crea los posts en Metricool (por defecto como BORRADOR, para que
                             nada salga en vivo sin una última revisión humana).

ADJUNTO DE VÍDEO (validado 27/07/2026):
  Si `metricool.json` se generó con `calendario.py --videos-json` (lleva el `drive_id` de cada
  vídeo), este script descarga el vídeo de Drive y lo sube a Metricool, adjuntándolo como REEL
  (ver `subir_media.py` y la memoria `metricool-subida-video`). Si un post no lleva `drive_id`,
  se crea solo con texto. --confirmar crea BORRADORES por defecto; nada se publica sin --publicar.
  No se activa en cron; lo lanza Winy tras el OK explícito de Gerard (Gate 3).

YOUTUBE SHORTS (21/08/2026):
  Las redes de cada cliente salen de `config/metricool-marcas.json`. Si entre ellas está
  `youtube`, cada post necesita `yt_titulo` (el gancho que se ve como título del Short; el
  caption no vale). Se manda como `youtubeData`, que además lleva:
    - `category` y `madeForKids` -> del bloque `youtube` del cliente en marcas.json
      (Xavi: SPORTS y false = "no creado para niños").
    - `tags` -> se sacan SOLOS de los hashtags del copy (`tags_de_texto`). No hay que
      escribirlas aparte; si aun así quieres forzarlas, pon `yt_tags` en el post.

TEXTO DEL POST:
  El caption es `post["texto"]` (el copy de Coco, escrito desde el copy-brief del cliente). Si el
  post no trae `texto`, cae al `titulo` corto (comportamiento antiguo). El preview marca ✍️ los
  que llevan copy y avisa de los que irían solo con el título.

AUTOPUBLICAR (21/08/2026):
  Por defecto se crean BORRADORES. Si el cliente lleva `autopublicar: true` en
  `config/metricool-marcas.json`, se crean EN FIRME y Metricool los saca solo a su hora
  (`draft=false` + `autoPublish=true`, también en `instagramData`). Xavi va así por decisión
  de Gerard. Con esto NO queda revisión humana entre el copy y la publicación: el preview lo
  avisa en rojo.

AVISO POR EMAIL:
  Tras crear los borradores con --confirmar, se envía a Gerard un email con el enlace al planner
  de cada borrador (reutiliza notifier/send_email.py; si falta SMTP no rompe nada, solo no avisa).

Uso:
  programar.py --in <dir_con_metricool.json> [--confirmar] [--publicar]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
API = "https://app.metricool.com/api"
TZ = "Europe/Madrid"

sys.path.insert(0, os.path.join(HUB, "infra/metricool"))
import subir_media  # noqa: E402  (descarga de Drive + subida a Metricool)


def load_env():
    env = {}
    with open(os.path.join(HUB, "infra/.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


def ajustes_youtube(cliente):
    """Ajustes fijos del post de YouTube del cliente: `youtube` en config/metricool-marcas.json.
    Devuelve {} si el cliente no tiene (entonces solo se manda título/tipo/privacidad)."""
    try:
        with open(os.path.join(HUB, "config/metricool-marcas.json"), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    for grupo in ("roster_v1", "fuera_de_roster_v1"):
        entrada = (data.get(grupo) or {}).get(cliente)
        if isinstance(entrada, dict) and isinstance(entrada.get("youtube"), dict):
            return entrada["youtube"]
    return {}


def autopublica(cliente):
    """¿Este cliente publica solo? `autopublicar` en config/metricool-marcas.json.

    Con true, sus posts se crean EN FIRME (draft=false + autoPublish=true) y Metricool los
    saca a su hora sin que nadie los revise. Xavi va así desde el 21/08/2026, por decisión
    de Gerard. El resto sigue creando borradores.
    """
    try:
        with open(os.path.join(HUB, "config/metricool-marcas.json"), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False
    for grupo in ("roster_v1", "fuera_de_roster_v1"):
        entrada = (data.get(grupo) or {}).get(cliente)
        if isinstance(entrada, dict):
            return bool(entrada.get("autopublicar"))
    return False


def tags_de_texto(texto, tope=500):
    """Etiquetas de YouTube a partir de los hashtags del copy (Gerard, 21/08/2026).

    Regla mecánica, para que nadie tenga que escribirlas dos veces: se cogen los hashtags del
    caption en su orden, se les quita la almohadilla y el CamelCase se parte en palabras
    (`#GloboEnPadel` -> "globo en padel"), que es como funciona una etiqueta de YouTube.
    Se cortan a `tope` caracteres en total, que es el límite de YouTube.
    """
    tags, vistos, total = [], set(), 0
    for bruto in re.findall(r"#(\w+)", texto or ""):
        partes = re.findall(r"[A-ZÁÉÍÓÚÑ]?[a-záéíóúñ]+|\d+|[A-ZÁÉÍÓÚÑ]+(?![a-z])", bruto)
        tag = " ".join(partes).lower().strip() or bruto.lower()
        if tag in vistos:
            continue
        if total + len(tag) + 1 > tope:
            break
        vistos.add(tag)
        tags.append(tag)
        total += len(tag) + 1
    return tags


def preview(data):
    posts = data.get("posts", [])
    print(f"Cliente: {data.get('cliente')}  ·  {len(posts)} publicaciones  ·  generado {data.get('generado')}")
    if autopublica(data.get("cliente")):
        print("🚨 AUTOPUBLICAR ACTIVADO: estos posts NO son borradores. Se crean en firme y\n"
              "   Metricool los publica solo a su hora. No hay revisión después de esto.")
    for p in posts:
        redes = "+".join(p.get("redes", []))
        video = " 🎬" if p.get("drive_id") else ""
        copy = " ✍️" if p.get("texto") else ""
        copy += " 🧪 Trial Reel" if p.get("ig_tipo") == "TRIAL_REEL" else ""
        copy += f" 🖼️ {p['portada_ms']}ms" if p.get("portada_ms") is not None else ""
        yt = ""
        if "youtube" in (p.get("redes") or []):
            yt = f" 📺 «{p['yt_titulo']}»" if p.get("yt_titulo") else " 📺 ⚠️ SIN TÍTULO"
        print(f"  {p['fecha']} {p.get('hora','15:00')} · {redes} · {p['titulo']}{video}{copy}{yt}")
    faltan_brand = [p for p in posts if not p.get("brand_id")]
    if faltan_brand:
        print(f"⚠️ {len(faltan_brand)} sin brand_id (revisa config/metricool-marcas.json).")
    con_video = sum(1 for p in posts if p.get("drive_id"))
    sin_video = len(posts) - con_video
    print(f"Vídeos: {con_video} con vídeo (🎬) · {sin_video} sin vídeo"
          + (" (solo texto — genera el metricool.json con --videos-json para adjuntarlos)" if sin_video else ""))
    sin_portada = [p for p in posts if p.get("drive_id") and p.get("portada_ms") is None]
    if sin_portada:
        print(f"⚠️ {len(sin_portada)} vídeo(s) SIN portada elegida (portada_ms): Metricool pondrá "
              "un fotograma cualquiera. Elígela con infra/programacion/portada.py.")
    con_copy = sum(1 for p in posts if p.get("texto"))
    sin_copy = len(posts) - con_copy
    print(f"Copy: {con_copy} con copy (✍️) · {sin_copy} sin copy"
          + (" (saldrían con el título como texto — falta el copy de Coco)" if sin_copy else ""))
    # YouTube exige título propio: sin él, crear_post() se planta antes de subir el vídeo.
    sin_yt = [p for p in posts if "youtube" in (p.get("redes") or []) and not p.get("yt_titulo")]
    if sin_yt:
        print(f"⚠️ {len(sin_yt)} van a YouTube SIN título (yt_titulo). No se crearán: "
              "escríbelos en el videos.json.")


def crear_post(env, post, publicar):
    """Crea UN post en Metricool (draft por defecto). Si el post lleva `drive_id`, descarga el
    vídeo de Drive, lo sube a Metricool y lo adjunta como REEL. Devuelve (ok, detalle)."""
    tok = env.get("METRICOOL_API_TOKEN")
    uid = env.get("METRICOOL_USER_ID")
    if not tok or not uid:
        return False, "faltan METRICOOL_API_TOKEN / METRICOOL_USER_ID en infra/.env"
    if not post.get("brand_id"):
        return False, "sin brand_id"

    redes = post.get("redes", [])
    # `publicar` llega por --publicar o por `autopublicar` del cliente (ver autopublica()).
    texto = post.get("texto") or post["titulo"]  # copy de Coco; si falta, el título (compat.)
    # YouTube no se conforma con el caption: exige TÍTULO propio. Sin él el post saldría con el
    # nombre del archivo, así que se corta aquí antes de subir el vídeo (Gerard, 21/08/2026).
    if "youtube" in redes and not post.get("yt_titulo"):
        return False, "falta yt_titulo (YouTube exige título; escríbelo en videos.json)"
    payload = {
        "text": texto,
        "publicationDate": {"dateTime": f"{post['fecha']}T{post.get('hora','15:00')}:00", "timezone": TZ},
        "providers": [{"network": n} for n in redes],
        "draft": not publicar,
        "autoPublish": bool(publicar),
    }
    if "youtube" in redes:
        yt = {"title": post["yt_titulo"][:100], "type": "SHORT", "privacy": "PUBLIC"}
        # Audiencia y categoría son fijas del cliente; las etiquetas salen del propio copy.
        yt.update(ajustes_youtube(post.get("cliente")))
        tags = post.get("yt_tags") or tags_de_texto(texto)
        if tags:
            yt["tags"] = tags
        payload["youtubeData"] = yt

    # Adjunto de vídeo: si el post trae drive_id, sube el vídeo a Metricool y añádelo a `media`.
    detalle_media = ""
    if post.get("drive_id"):
        try:
            media_url = subir_media.subir_video_de_drive(env, post["brand_id"], post["drive_id"])
        except Exception as e:  # noqa: BLE001  (si el vídeo falla, no creamos un post sin vídeo)
            return False, f"subiendo vídeo: {e}"
        payload["media"] = [media_url]
        # Portada (Gerard, 09/10/2026): el fotograma donde se lee el texto principal. Se elige
        # mirando el vídeo con infra/programacion/portada.py y va en el post como `portada_ms`.
        if post.get("portada_ms") is not None:
            payload["videoCoverMilliseconds"] = int(post["portada_ms"])
        if "instagram" in redes:
            # IG exige el tipo para vídeo; y su autoPublish es un flag aparte del general.
            payload["instagramData"] = {"type": "REEL", "autoPublish": bool(publicar)}
            # Trial Reel (02/10/2026): `"ig_tipo": "TRIAL_REEL"` en el post. Solo lo ven no
            # seguidores; no se comparte solo con los seguidores (eso lo decide Gerard después).
            if post.get("ig_tipo") == "TRIAL_REEL":
                payload["instagramData"].update({"type": "TRIAL_REEL", "shareTrialAutomatically": False})
        detalle_media = " +vídeo"

    q = f"blogId={post['brand_id']}&userId={uid}"
    req = urllib.request.Request(
        f"{API}/v2/scheduler/posts?{q}",
        data=json.dumps(payload).encode(),
        headers={"X-Mc-Auth": tok, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            cuerpo = resp.read().decode(errors="replace")
            post["_enlace"] = enlace_planner(post["brand_id"], cuerpo)  # para el email de aviso
            return True, f"{resp.status}{detalle_media}"
    except urllib.error.HTTPError as e:
        return False, f"{e.code}: {e.read().decode(errors='replace')[:300]}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return "".join(c if c.isalnum() else " " for c in s).split()


def marcar_en_notion(cliente, titulo, fecha):
    """Best-effort: refleja en Notion que este post ya está programado.

    Busca en la base del cliente una fila en `Producción = Editado` cuyo título case con el del
    vídeo y, SOLO si hay una única coincidencia, la deja en `Producción = Programado` con la fecha
    en `Publicación`. Si hay 0 o varias, no toca nada (mejor no marcar que marcar la equivocada).
    Todo bajo try: un fallo de Notion nunca debe romper la programación en Metricool.
    """
    try:
        sys.path.insert(0, os.path.join(HUB, "infra/notion"))
        import notion_api as na
        tok = na.token()
        cli = na.load_config()["clientes"].get(cliente)
        if not cli:
            return ""
        filas = na.query(cli["database_id"], tok,
                         {"property": "Producción", "select": {"equals": "Editado"}})
        objetivo = set(_norm(titulo))
        cand = []
        for f in filas:
            palabras = set(_norm(na.plain(f["properties"].get("Idea"))))
            if palabras and objetivo and (palabras == objetivo or objetivo <= palabras
                                          or palabras <= objetivo):
                cand.append(f)
        if len(cand) != 1:
            return f" (Notion: {len(cand)} coincidencias, no marco)"
        na.update_props(cand[0]["id"], tok, {
            "Producción": na.prop_select("Programado"),
            "Publicación": na.prop_date(fecha),
        })
        return " → Notion: Programado"
    except Exception as e:  # noqa: BLE001
        return f" (Notion no actualizado: {e})"


def enlace_planner(brand_id, cuerpo):
    """Construye el enlace al planner de Metricool para el post recién creado. Intenta sacar el
    id del post de la respuesta; si no lo encuentra, devuelve el planner de la marca (fallback)."""
    base = f"https://app.metricool.com/planning/list?blogId={brand_id}"
    try:
        data = json.loads(cuerpo)
        d = data.get("data", data) if isinstance(data, dict) else {}
        pid = d.get("id") or d.get("postId") or d.get("uuid")
        if pid:
            return f"{base}&postId={pid}"
    except Exception:  # noqa: BLE001
        pass
    return base


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="indir", required=True, help="Directorio con metricool.json")
    p.add_argument("--confirmar", action="store_true", help="Crea los posts (si no, solo preview)")
    p.add_argument("--publicar", action="store_true",
                   help="Crea en firme en vez de borrador (por defecto: borrador)")
    p.add_argument("--sin-aviso", dest="sin_aviso", action="store_true",
                   help="No manda el email con los enlaces. Úsalo SIEMPRE que Gerard esté "
                        "pidiendo esto en la conversación: ya lo sabe, el correo sobra "
                        "(regla suya, 22/09/2026).")
    p.add_argument("--notion", action="store_true",
                   help="Refleja en Notion (Producción=Programado + Publicación) la fila que case "
                        "por título. Solo marca si hay coincidencia única; opt-in.")
    a = p.parse_args()

    ruta = os.path.join(a.indir, "metricool.json")
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.stderr.write(f"No encuentro {ruta}. ¿Corriste calendario.py --out ese directorio?\n")
        return 2

    preview(data)
    if not a.confirmar:
        print("\n(preview — no he tocado Metricool. Añade --confirmar tras el OK de Gerard.)")
        return 0

    env = load_env()
    # En firme por --publicar o porque el cliente tenga `autopublicar` en marcas.json.
    publicar = a.publicar or autopublica(data.get("cliente"))
    modo = "EN FIRME — se publican solos" if publicar else "como BORRADOR"
    print(f"\nCreando en Metricool ({modo})...")
    ok_n = 0
    creados = []  # para el email: (fecha, titulo, enlace)
    for post in data.get("posts", []):
        ok, detalle = crear_post(env, post, publicar)
        if ok and a.notion:
            detalle += marcar_en_notion(data.get("cliente", ""), post["titulo"], post["fecha"])
        marca = "✅" if ok else "❌"
        print(f"  {marca} {post['fecha']} {post['titulo']} — {detalle}")
        if ok:
            ok_n += 1
            creados.append((post["fecha"], post["titulo"], post.get("_enlace", "")))
    print(f"\n{ok_n}/{len(data.get('posts', []))} creados.")

    if creados:
        if not a.sin_aviso:
            avisar_email(env, data.get("cliente", ""), modo, creados, publicar)
    return 0 if ok_n else 1


def avisar_email(env, cliente, modo, creados, publicar=False):
    """Manda a Gerard un email con el enlace a cada borrador creado. Reutiliza send_email.py.
    Si falta SMTP (o falla), no rompe: solo deja aviso en stderr."""
    destino = env.get("EMAIL_DESTINO")
    if not destino or not (env.get("SMTP_USER") and env.get("SMTP_PASS")):
        sys.stderr.write("(email no configurado: SMTP_USER/SMTP_PASS/EMAIL_DESTINO — no aviso)\n")
        return
    lineas = [f"{fecha} · {titulo}\n{enlace}" for fecha, titulo, enlace in creados]
    if publicar:
        cuerpo = (f"Posts creados EN FIRME en Metricool para {cliente}.\n"
                  "Se publican SOLOS en su fecha: si algo no te cuadra, edítalo o bórralo "
                  "en el planner ANTES de esa fecha.\n\n" + "\n\n".join(lineas))
        asunto = f"Metricool · {len(creados)} post(s) EN FIRME {cliente} — se publican solos"
    else:
        cuerpo = (f"Borradores creados en Metricool ({modo}) para {cliente}:\n\n"
                  + "\n\n".join(lineas)
                  + "\n\nRevísalos/edítalos en el planner antes de publicar.")
        asunto = f"Metricool · {len(creados)} borrador(es) {cliente}"
    entorno = dict(os.environ)
    entorno.update({
        "SMTP_USER": env.get("SMTP_USER", ""), "SMTP_PASS": env.get("SMTP_PASS", ""),
        "MAIL_TO": destino, "MAIL_SUBJECT": asunto, "MAIL_BODY": cuerpo,
    })
    for opt in ("SMTP_HOST", "SMTP_PORT"):
        if env.get(opt):
            entorno[opt] = env[opt]
    script = os.path.join(HUB, "infra/notifier/send_email.py")
    r = subprocess.run(["/usr/bin/python3", script], env=entorno,
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"📧 Email con el enlace enviado a {destino}.")
    else:
        sys.stderr.write(f"(no se pudo enviar el email: {r.stderr.strip()})\n")


if __name__ == "__main__":
    raise SystemExit(main())
