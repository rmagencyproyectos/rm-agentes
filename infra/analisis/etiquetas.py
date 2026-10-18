#!/usr/bin/env python3
"""Lector de las etiquetas. Se importa; no es un CLI.

Dos archivos, cada uno con lo suyo (02/10/2026), para que nada viva en dos sitios:
  - `agentes/guiones/ETIQUETAS.md`  — FUENTE ÚNICA de las listas cerradas comunes (Tipo de
    idea, Formato, Palanca, Soporte) y de su definición. Lo escribe y lo lee una persona.
  - `config/etiquetas.json`          — solo lo que ETIQUETAS.md no tiene: etiquetas propias de
    cada cliente, lo que el etiquetado automático no usa, dónde se escriben y lo pendiente.
  - Plantilla: la carpeta `agentes/guiones/plantillas/`.

Las listas se sacan de las tablas del .md (cada fila empieza por la opción entre `backticks`)
y de las líneas "`A` · `B` · `C`" de Palanca y Soporte. Si alguien cambia ese formato, esto
falla en voz alta en vez de devolver listas vacías.
"""
import json
import os
import re

HUB = "/Users/gerardruizmiro/rmagency/AGENTES RM"
MD = os.path.join(HUB, "agentes/guiones/ETIQUETAS.md")
JSON = os.path.join(HUB, "config/etiquetas.json")
PLANTILLAS = os.path.join(HUB, "agentes/guiones/plantillas")
SECCIONES = ("Tipo de idea", "Formato", "Palanca", "Soporte")


def _secciones(texto):
    out, actual = {}, None
    for linea in texto.splitlines():
        m = re.match(r"^## (.+?)\s+—", linea)
        if m:
            actual = m.group(1).strip()
            out[actual] = []
        elif linea.startswith("## ") or linea.startswith("---"):
            actual = None
        elif actual:
            out[actual].append(linea)
    return out


def listas():
    with open(MD, encoding="utf-8") as f:
        sec = _secciones(f.read())
    out = {}
    for nombre in SECCIONES:
        lineas = sec.get(nombre, [])
        filas = [m.group(1) for l in lineas for m in [re.match(r"^\|\s*`([^`]+)`\s*\|", l)] if m]
        if not filas:   # Palanca / Soporte: el primer PÁRRAFO que es "`A` · `B` · …" (puede ocupar 2 líneas)
            parrafos, actual_p = [], []
            for l in lineas + [""]:
                if l.strip():
                    actual_p.append(l)
                elif actual_p:
                    parrafos.append(" ".join(actual_p))
                    actual_p = []
            lista = next((p for p in parrafos if "·" in p and p.lstrip().startswith("`")), "")
            filas = re.findall(r"`([^`]+)`", lista)
        if not filas:
            raise RuntimeError(f"ETIQUETAS.md: no encuentro la lista de «{nombre}»")
        out[nombre] = filas
    out["Plantilla"] = sorted(f[:-3] for f in os.listdir(PLANTILLAS)
                              if f.endswith(".md") and not f.startswith(("_", "README")))
    return out


def glosario():
    """{dimensión: {opción: qué es, en una frase}} para enseñarlo en el panel.
    Tipo de idea, Formato y Palanca: la columna "Es esto" de las tablas de ETIQUETAS.md.
    Plantilla: el subtítulo del H1 de cada plantilla ("# caso-real — un encargo, de principio a fin")."""
    with open(MD, encoding="utf-8") as f:
        sec = _secciones(f.read())
    out = {}
    for nombre in ("Tipo de idea", "Formato", "Palanca"):
        out[nombre] = {m.group(1): m.group(2).strip()
                       for l in sec.get(nombre, [])
                       for m in [re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+)\|", l)] if m}
    out["Plantilla"] = {}
    for p in listas()["Plantilla"]:
        with open(os.path.join(PLANTILLAS, p + ".md"), encoding="utf-8") as f:
            h1 = f.readline().strip()
        out["Plantilla"][p] = h1.split("—", 1)[1].strip() if "—" in h1 else ""
    return out


def definiciones():
    """El texto de las secciones de listas + desempates, tal cual, para dárselo a un modelo."""
    with open(MD, encoding="utf-8") as f:
        texto = f.read()
    ini = texto.find("## Tipo de idea")
    fin = texto.find("## Lo que se movió")
    return texto[ini:fin if fin > 0 else None].strip()


def config():
    with open(JSON, encoding="utf-8") as f:
        return json.load(f)


def listas_automaticas():
    """Las listas menos lo que el etiquetado automático no debe usar (`no_inferir`)."""
    fuera = config().get("no_inferir", {})
    return {k: [x for x in v if x not in fuera.get(k, [])] for k, v in listas().items()}
