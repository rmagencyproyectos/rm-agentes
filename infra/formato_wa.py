#!/usr/bin/env python3
"""Normaliza texto de Markdown a formato WhatsApp. Filtro de stdin a stdout.

Los modelos escriben Markdown por costumbre (`**negrita**`, `## títulos`), y WhatsApp usa
otra sintaxis: la negrita es con UN asterisco y no hay encabezados. Pedírselo en el prompt
ayuda, pero no es fiable al 100%; esto lo arregla siempre y gratis.

  **negrita**  -> *negrita*
  __negrita__  -> *negrita*
  ## Título    -> *Título*
  - viñeta     -> • viñeta
"""
import re
import sys


def normaliza(t):
    # Negrita de Markdown -> negrita de WhatsApp (un solo asterisco)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"*\1*", t, flags=re.S)
    t = re.sub(r"\*\*(.+?)\*\*", r"*\1*", t, flags=re.S)
    t = re.sub(r"___(.+?)___", r"*\1*", t, flags=re.S)
    t = re.sub(r"__(.+?)__", r"*\1*", t, flags=re.S)
    out = []
    for ln in t.splitlines():
        # Encabezados de Markdown -> línea en negrita
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", ln)
        if m:
            ln = f"*{m.group(1)}*" if m.group(1) else ""
        # Viñetas "-" / "*" al principio de línea -> "•" (deja intactas las "- [ ]")
        m = re.match(r"^(\s*)[-*]\s+(?!\[[ xX]\])(.*)$", ln)
        if m:
            ln = f"{m.group(1)}• {m.group(2)}"
        out.append(ln.rstrip())
    t = "\n".join(out)
    # Como mucho una línea en blanco seguida
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


if __name__ == "__main__":
    sys.stdout.write(normaliza(sys.stdin.read()))
