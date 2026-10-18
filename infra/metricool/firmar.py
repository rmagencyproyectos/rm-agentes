#!/usr/bin/env python3
"""Pasa un post de Metricool de BORRADOR a EN FIRME (se publica solo a su hora).

Hasta el 22/09/2026 el sistema solo sabía CREAR borradores (`programar.py`): pasarlos a firme
era siempre clic de Gerard en el planner. Esto existe para cuando Gerard lo pide explícitamente
("prográmalo ya"), sin tener que borrar el borrador y volver a crearlo (que reubicaría el vídeo).

⚠️ GATE: esto hace que el vídeo se publique SOLO. No se corre por iniciativa propia ni desde un
automatismo: solo cuando Gerard lo pide para una pieza concreta. Los clientes con
`autopublicar` en `config/metricool-marcas.json` (Xavi) ya nacen en firme y no necesitan esto.

Uso:
  firmar.py --cliente jesus-mora --fecha 2026-09-23 [--dry-run]
  firmar.py --cliente jesus-mora --id 380247204
Salida: 0 ok · 1 error · 2 falta configuración
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/Users/gerardruizmiro/rmagency/AGENTES RM/infra/metricool")
sys.path.insert(0, "/Users/gerardruizmiro/rmagency/AGENTES RM/infra/programacion")
import calendario as cal  # noqa: E402
import chequeo_cobertura as cob  # noqa: E402

API = "https://app.metricool.com/api"


def pedir(metodo, path, tok, payload=None):
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"X-Mc-Auth": tok, "Content-Type": "application/json", "Accept": "application/json"},
        method=metodo)
    with urllib.request.urlopen(req, timeout=90) as resp:
        cuerpo = resp.read().decode(errors="replace")
        return json.loads(cuerpo) if cuerpo else {}


def main():
    p = argparse.ArgumentParser(description="Pasa un borrador de Metricool a firme.")
    p.add_argument("--cliente", required=True)
    p.add_argument("--fecha", help="YYYY-MM-DD: firma los borradores de ese día.")
    p.add_argument("--id", type=int, help="Id del post concreto.")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if not a.fecha and not a.id:
        sys.stderr.write("Dime --fecha o --id.\n")
        return 2

    env = cob.load_env()
    tok, uid = env.get("METRICOOL_API_TOKEN"), env.get("METRICOOL_USER_ID")
    bid = cal.brand_id(a.cliente)
    if not (tok and uid and bid):
        sys.stderr.write("Faltan credenciales de Metricool o la marca del cliente.\n")
        return 2

    dia = datetime.date.fromisoformat(a.fecha) if a.fecha else datetime.date.today()
    # Con --id y sin --fecha no sabemos el día: se busca en los próximos 60 (antes miraba solo
    # hoy y nunca encontraba un post programado para otro día).
    dias = 1 if a.fecha else 60
    posts = cob.get_programados(bid, uid, tok, dia, dia + datetime.timedelta(days=dias)) or []
    objetivo = [x for x in posts if (x.get("id") == a.id if a.id else x.get("draft"))]
    if not objetivo:
        print("No hay borradores que firmar ahí.")
        return 0

    fallos = 0
    for post in objetivo:
        titulo = (post.get("text") or "")[:60].replace("\n", " ")
        if a.dry_run:
            print(f"(dry-run) firmaría {post['id']}: {titulo}")
            continue
        # Solo los campos editables: si se reenvía el post tal cual, la API devuelve 500 por
        # los de solo lectura (`providers[].status`, `detailedStatus`…).
        cuerpo = {
            "id": post["id"],
            "text": post.get("text") or "",
            "publicationDate": post.get("publicationDate"),
            "providers": [{"network": pr["network"]} for pr in post.get("providers", [])],
            "media": post.get("media") or [],
            "draft": False,
            "autoPublish": True,
        }
        # La portada elegida (videoCoverMilliseconds) se pierde si no se reenvía al firmar.
        for clave in ("videoCoverMilliseconds", "videoThumbnailUrl"):
            if post.get(clave) is not None:
                cuerpo[clave] = post[clave]
        for clave in ("instagramData", "youtubeData", "tiktokData", "facebookData"):
            datos = post.get(clave)
            if isinstance(datos, dict):
                limpio = {k: v for k, v in datos.items() if k not in ("status", "detailedStatus")}
                if clave == "instagramData":
                    limpio["autoPublish"] = True
                cuerpo[clave] = limpio
        try:
            pedir("PUT", f"/v2/scheduler/posts/{post['id']}?blogId={bid}&userId={uid}", tok, cuerpo)
            print(f"✅ en firme: {post['id']} · {(post.get('publicationDate') or {}).get('dateTime','')} · {titulo}")
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"✗ {post['id']}: {e.code} {e.read().decode(errors='replace')[:300]}\n")
            fallos += 1
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"✗ {post['id']}: {e}\n")
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
