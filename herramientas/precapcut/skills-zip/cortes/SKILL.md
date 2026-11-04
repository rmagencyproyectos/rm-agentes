---
name: "cortes"
description: "Fase 1 de pre-edición en CapCut: quita tomas falladas, arranques en falso, muletillas y silencios de vídeos en bruto y monta los cortes en CapCut con precapcut."
---

# Cortes (fase 1 de precapcut)

Deja en CapCut el vídeo de un cliente hablando a cámara ya cortado: sin tomas falladas, sin arranques en falso, sin muletillas y sin silencios. Gerard revisa antes de pasar a la fase 2 (subtítulos).

## Dónde está la herramienta

- Mac de Gerard: `~/rmagency/AGENTES RM/herramientas/precapcut/`.
- Otros ordenadores: la carpeta `herramientas/precapcut/` del repositorio `rmagencyproyectos/rm-agentes`. Si no está instalada, ejecuta `bash instalar-mac.sh` o `instalar-windows.ps1`.
- Lee `LEEME.md` de esa carpeta antes de empezar: allí están el flujo completo y los ajustes.

## Pasos

1. Pide (o deduce) los vídeos en bruto en orden de grabación y el proyecto de CapCut de destino. Si Gerard creó un proyecto vacío, usa `--en`; si no, usa `--nuevo`.
2. `python3 precapcut.py fase1 <pieza> <vídeos...> [--idioma es|ca]`. `<pieza>` es un nombre corto sin espacios, como `cliente-AAAA-MM-DD`.
3. Lee **solo** `~/rmagency/work/precapcut/<pieza>/fase1.md`. No abras nunca el vídeo, `transcripciones.json` ni el JSON del proyecto de CapCut, porque gastan muchos tokens. Revisa con criterio:
   - Si dos frases dicen lo mismo con otras palabras, quédate con la mejor (normalmente la última).
   - Saca la charla fuera de guion («¿grabas?», «otra vez», «¿aquí o no?»).
   - Para cambiar una decisión, edita `decisiones.json` con un script corto (`queda` y `"a_mano": true`).
4. Comprueba que CapCut está **cerrado** (`pgrep -x CapCut`). Si está abierto, pide a Gerard que lo cierre y no lo mates nunca. Después ejecuta `python3 precapcut.py montar <pieza> --en "<proyecto>"` (o `--nuevo "<nombre>"`). La herramienta hace una copia de seguridad y deja los clips apuntando al vídeo original entero, para que Gerard pueda alargarlos.
5. QA propio, que es obligatorio: ejecuta `python3 precapcut.py qa <pieza>` y lee `qa-fase1.md`. No puede quedar ningún corte que entre o salga con sonido, ninguna palabra comida ni ninguna pausa larga. Si algo falla, ajústalo y vuelve a montar.
6. Avisa a Gerard en pocas líneas: duración en bruto y montada, número de cortes, tomas descartadas, frases dudosas y el nombre del proyecto que tiene que abrir. **Espera su OK antes de la fase 2.**

## Reglas

- Si Gerard ya ha tocado el proyecto a mano, no vuelvas a montar encima. Las fases siguientes solo añaden pistas.
- No subas el audio a ningún servicio: la transcripción se hace en local con faster-whisper.
- CapCut está congelado en la 9.5, porque la 10 rechaza estos proyectos.
- Los nombres que salgan mal se añaden a `vocabulario.txt`.
- Para material POV sin voz (resumen de mejores momentos), esta fase no sirve. Eso se hace eligiendo planos con hojas de contacto.