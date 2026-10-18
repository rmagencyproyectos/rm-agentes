#!/usr/bin/env python3
"""Carril 0 — responde SIN llamar a Claude (0 tokens).

Solo atiende preguntas cuya respuesta es calculable a partir del estado del sistema
(cobertura, estado de los ciclos, ayuda). Todo lo demás lo deja pasar al carril 1 (Winy
conversacional en Haiku).

Es DELIBERADAMENTE conservador: ante la duda, no contesta. Un falso positivo aquí le
suelta a Gerard una plantilla donde esperaba una conversación, así que solo dispara con
preguntas explícitas de consulta y nunca si el mensaje pide *hacer* algo.

Uso:  router.py "<mensaje>"
      -> imprime la respuesta y sale 0   (atendido, no hace falta modelo)
      -> no imprime nada y sale 1        (que lo coja el carril 1)
"""
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import estado as est  # noqa: E402  (mismo directorio)


def normaliza(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


# Si el mensaje pide EJECUTAR algo, no es una consulta: que lo coja el modelo.
# `recuerdame` NO está aquí: los recordatorios simples los captura `capturar_recordatorio`
# (0 tokens) antes de esta comprobación; los que traen fecha/cliente sí escalan al modelo.
ACCIONES = re.compile(
    r"\b(apunta|apuntame|anota|cambia|cambiame|actualiza|arregla|corrige|modifica|pon|ponme|"
    r"quita|borra|elimina|crea|crea me|haz|hazme|dile|diles|manda|envia|programa|marca|"
    r"escribe|guarda|añade|agrega|prepara|genera|monta|edita|renombra|mueve)\b"
)

# --- Captura barata de recordatorios (0 tokens) -------------------------------------
# Solo la familia "recuérdame ...": es inequívocamente un recordatorio (a diferencia de
# "apunta/anota", que pueden ser una idea de contenido para Notion y por eso las lleva el
# modelo). Si el texto trae una fecha relativa o un #cliente, se deja escalar para que el
# modelo lo estructure con '📅 YYYY-MM-DD' / '#cliente'.
CAPTURA = re.compile(r"^(recuerdame|recordarme|recuerda)\b")
ESTRUCTURAR = re.compile(
    r"\b(hoy|manana|pasado|lunes|martes|miercoles|jueves|viernes|sabado|domingo|"
    r"la semana|el mes|a las|antes de|el dia|proximo|proxima)\b|#\w+"
)
_QUITA_VERBO = re.compile(r"^\s*(recu[eé]rdame|recordarme|recuerda)\b[:\s]*", re.IGNORECASE)

# Preguntas de cobertura / programación
COBERTURA = re.compile(
    r"\b(cobertura|programad[oa]s?|programacion|que falta por programar|"
    r"esta todo programado|huecos)\b"
)

# Preguntas de estado general
AYUDA = re.compile(
    r"\b(que sabes hacer|que puedes hacer|que haces|en que me puedes ayudar|"
    r"ayuda|comandos|opciones)\b"
)

TEXTO_AYUDA = """Esto es lo que puedo hacer por ti:

*Consultas rápidas* (te contesto al momento)
• "¿cómo va la cobertura?" — qué falta por programar
• "¿qué hay pendiente?" — cómo van los ciclos
• "ayuda" — esto mismo

*Cosas que te hago*
• Apuntar notas y recordatorios
• Mirar cómo va un cliente concreto
• Despachar trabajo a los agentes (editor, estratega…)
• Cambios en el sistema (te lo propongo antes de tocar nada)

*Lo que NO hago* 🔔
• Mandar nada a clientes ni programar en Metricool — eso lo aprietas tú

Escríbeme o mándame un audio, como te sea más cómodo 🙌"""


def responde_cobertura():
    cuerpo = est.leer_cobertura(refrescar=False)
    return cuerpo


def capturar_recordatorio(original, m):
    """Apunta un 'recuérdame ...' simple en la bandeja y confirma. 0 tokens.

    Devuelve el texto de confirmación si lo captura, o None para que lo coja otro carril
    (no es un recordatorio, trae fecha/cliente que hay que estructurar, o no se pudo escribir).
    """
    if not CAPTURA.search(m):
        return None
    if ESTRUCTURAR.search(m):
        return None  # tiene fecha o #cliente: que lo estructure el modelo
    texto = _QUITA_VERBO.sub("", original).strip()
    if not texto:
        return None
    try:
        ruta = os.path.join(est.VAULT, "notas", "📥 Bandeja.md")
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"- [ ] {texto}\n")
    except Exception:
        return None  # si no se puede escribir, que lo coja el modelo
    return f"✅ Apuntado: {texto}"


def resolver(msg):
    m = normaliza(msg)
    if not m:
        return None
    cap = capturar_recordatorio(msg, m)
    if cap is not None:
        return cap
    if ACCIONES.search(m):
        return None
    # Mensajes largos suelen ser contexto/conversación, no una consulta seca.
    if len(m) > 160:
        return None
    if AYUDA.search(m):
        return TEXTO_AYUDA
    if COBERTURA.search(m):
        return responde_cobertura()
    # "¿cómo va todo?" / "qué hay pendiente" ya NO se responden aquí en crudo: se dejan caer al
    # carril del modelo (Haiku), que redacta el ESTADO con la voz de Winy (sin ladrillo ni jerga).
    return None


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else ""
    r = resolver(msg)
    if r is None:
        return 1
    sys.stdout.write(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
