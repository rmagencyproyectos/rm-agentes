#!/usr/bin/env python3
"""Sube la tanda de Oli a la Bandeja de Ideas RM, marcada `Autor = Oli`, para que Gerard la valide.

Por qué existe (22/09/2026): hasta ahora las ideas de Oli se quedaban en `hipotesis.json` y en
la pantalla de su sesión. No llegaban a Notion, así que o alguien las copiaba a mano o se
perdían, y además con títulos distintos a los de la tanda (por eso el termómetro no casaba
nunca una pieza de Oli con su publicación).

Ahora cada pieza entra en la Bandeja con:
  Estado Nueva · Autor Oli · Cliente · Tipo · Plantilla · Tipo de idea · Formato
  Origen "Oli · tanda <ciclo> · <id>" · Notas con la apuesta y el porqué
y con el MISMO título que en `hipotesis.json`. Gerard las ve juntas (vista "🤖 Propuestas de
Oli" o filtro Autor = Oli), aprueba las que quiera y siguen el camino normal (distribuir →
Coco → 🎬 A grabar). Las que descarte, las marca `Descartada` y se quedan en el histórico.

Idempotente: guarda el enlace de Notion en la pieza (`bandeja`) y no la vuelve a subir.

Uso:  a_bandeja.py <cliente> <YYYY-MM> [--dry-run]
Salida: 0 ok · 2 falta token · 1 error
"""
import argparse
import json
import os
import sys

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
sys.path.insert(0, os.path.join(HUB, "infra/notion"))
import etiquetas_idea as ei  # noqa: E402
import idea_add  # noqa: E402
import notion_api as na  # noqa: E402


def notas_de(pieza):
    partes = []
    for clave, etiqueta in (("apuesta", "Apuesta"), ("porque", "Por qué"),
                            ("notas", "Notas de Oli")):
        if pieza.get(clave):
            partes.append(f"{etiqueta}: {pieza[clave]}")
    return "\n".join(partes)


def main():
    ap = argparse.ArgumentParser(description="Sube la tanda de Oli a la Bandeja (Autor = Oli).")
    ap.add_argument("cliente")
    ap.add_argument("ciclo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    ruta = os.path.join(HUB, "ciclos", a.ciclo, a.cliente, "hipotesis.json")
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
    except (OSError, ValueError) as e:
        sys.stderr.write(f"No puedo leer {ruta}: {e}\n")
        return 1
    try:
        tok = na.token()
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    db = na.load_config()["bandeja"]["database_id"]

    subidas = 0
    for pieza in datos.get("piezas", []):
        if pieza.get("bandeja") or not pieza.get("titulo"):
            continue
        args = argparse.Namespace(
            idea=pieza["titulo"], cliente=a.cliente, tipo=pieza.get("tipo"),
            soporte=pieza.get("soporte"), origen=f"Oli · tanda {a.ciclo} · {pieza.get('id', '')}",
            referencia=pieza.get("referencia"), notas=notas_de(pieza),
            tipo_idea=pieza.get("tipo_idea"), formato=pieza.get("formato"),
            autor="Oli", plantilla=pieza.get("plantilla"), estado="Nueva")
        if args.tipo not in idea_add.TIPOS:
            args.tipo = None
        if args.soporte not in idea_add.SOPORTES:
            args.soporte = None
        if a.dry_run:
            print(f"(dry-run) subiría: {pieza['titulo'][:70]}  "
                  f"[{args.plantilla or '—'} · {args.formato or '—'} · {args.tipo_idea or '—'}]")
            continue
        try:
            pagina = na.create_page(db, tok, ei.traducir(idea_add.construir_propiedades(args), db, tok))
        except RuntimeError as e:
            sys.stderr.write(f"✗ {pieza['titulo'][:60]}: {e}\n")
            continue
        pieza["bandeja"] = pagina.get("url", "")
        subidas += 1
        print(f"✓ {pieza['titulo'][:70]}")

    if subidas:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
        print(f"\n{subidas} propuesta(s) de Oli en la Bandeja, Estado Nueva. Gerard las aprueba allí.")
    elif not a.dry_run:
        print("Nada nuevo que subir (ya estaban todas en la Bandeja).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
