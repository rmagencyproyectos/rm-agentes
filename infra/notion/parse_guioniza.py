#!/usr/bin/env python3
"""¿El mensaje de WhatsApp pide "guioniza ya" (urgencia) y para qué cliente?

Lo usa el carril 0.5 de infra/responder/process.sh. Imprime:
  ""       -> no es esta intención (sigue el flujo normal)
  "ALL"    -> guioniza ya, sin cliente concreto (todos los pendientes)
  "<slug>" -> guioniza ya ese cliente

Intención = raíz "guioniz" (guioniza/guionizar/guionízame…) + una palabra de urgencia
(ya/ahora/urgente/corriendo/volando). Así "ya tengo el guion" NO dispara nada.
"""
import re
import sys
import unicodedata


def _sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower())
                   if not unicodedata.combining(c))


CLIENTES = {
    "golossa": ["golossa"],
    "midtown": ["midtown"],
    "jesus-mora": ["jesus mora", "jesús mora", "jesusmora", "jesus", "jesús", "mora"],
    "newmos": ["newmos", "new mos"],
    "msm": ["msm models", "msm"],
    "xavi-colomina": ["xavi colomina", "colomina", "xavi"],
    "algoritmo": ["algoritmo"],
    "rm-agency": ["rm agency", "rm-agency", "rmagency", "la agencia", "nuestra cuenta"],
}


def main():
    msg = _sin_tildes(" ".join(sys.argv[1:]))
    urgente = re.search(r"\b(ya|ahora|urgente|urgent|corriendo|volando)\b", msg)
    if "guioniz" not in msg or not urgente:
        print("")
        return
    for slug, alias in CLIENTES.items():
        if any(_sin_tildes(a) in msg for a in alias):
            print(slug)
            return
    print("ALL")


if __name__ == "__main__":
    main()
