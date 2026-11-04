---
name: "sonidos"
description: "Fase 3 de pre-edición en CapCut: coloca efectos de sonido de la biblioteca de Gerard según lo que pasa en el vídeo (titulares, exclamaciones, CTA, preguntas) con precapcut."
---

# Fase 3 · Sonidos (precapcut)

Se usa con un proyecto de CapCut ya cortado (fase 1) y con textos (fase 2) aprobados. Herramienta: `~/rmagency/AGENTES RM/herramientas/precapcut/` (cómo funciona todo: `LEEME.md`). Trabajo en `~/rmagency/work/precapcut/<pieza>/`.

## Antes de empezar
- Leer `aprendizajes/general.md` y `aprendizajes/<cliente>.md`.
- **CapCut cerrado del todo (Cmd+Q)** antes de escribir: cerrar la ventana deja el proceso vivo.

## Pasos
1. `python3 precapcut.py sonidos <pieza> "<proyecto>" --estilo <cliente> --solo-md --regenerar` → leer **solo** `sonidos.md` (lee los tiempos REALES del proyecto). Revisar con criterio y ajustar `sonidos-decisiones.json` (cambiar `sonido`, borrar, `volumen`).
2. Sin `--solo-md` (CapCut cerrado): AÑADE pistas `Sonidos` (y `Sonidos 2…` si se solapan). Rehacer = quitar solo esas pistas. Copia de seguridad antes de escribir.
3. QA: cada efecto entero (sin cola cortada), voz inteligible en la mezcla, copias de rotoscopia siguen mudas (volumen 0 y pista silenciada).
4. Avisar a Gerard y esperar su OK.

## Biblioteca (la de Gerard, 03/11/2026)
19 sonidos de la biblioteca de CapCut que eligió él, en `sonidos/NN-<papel>.wav`, nombre GENÉRICO por cuándo usarlo (nunca por el vídeo de muestra). Lista y uso: `sonidos/biblioteca-gerard.md`.

- 01 foto: sale una foto o captura
- 02 transición: cambio de tema
- 03 whoosh: entra algo rápido
- 04 tiempo: plazos, esperas
- 05 chasquido: «así de fácil», cambio instantáneo
- 06 whoosh-corto
- 07 idea: truco, consejo
- 08 clic: CTA (guarda, sígueme, pulsa)
- 09 tensión: problema, suspense
- 10 error: algo mal hecho, negación
- 11 marcar: señalar algo en pantalla
- 12 silencio-incómodo: humor
- 13 dinero: precio, ahorro
- 14 sorpresa: resultado, revelación
- 15 impacto: exclamación, frase clave
- 17 correcto: solución, lo que sí
- 19 pop: cada titular que entra
- 18 riser (4 s) y 16 riser-corto (0,4 s): intriga al plantear una pregunta. Terminan justo cuando acaba la pregunta y empieza la respuesta. Máximo 2 por vídeo.

Para ampliarla: Gerard pone los sonidos en fila en el proyecto «Biblioteca sonidos RM» (una pista, 0,5 s de silencio entre ellos), exporta el audio y `python3 precapcut.py sonidos-cortar <archivo>`.

## Reglas de Gerard
- Un pop por titular (primera línea), no por línea. Nada en los subtítulos.
- Whoosh solo en cambios de plano reales, no en cada jump cut.
- Niveles: pops y efectos a 0 dB (volumen 1.0); whoosh y transiciones más bajos (~0.14).
- Nunca cortar la cola de un efecto.
- Sin efectos sintetizados ni de Mixkit (`sonidos/mixkit/`, `sonidos/sintetizados/` en desuso).
- Tips nuevos de Gerard, Andrea o Jaume → `aprendizajes/` (fecha y autor, sin borrar nada).