---
name: "recursos"
description: "Fase 2b de pre-edición en CapCut: añade animaciones sin texto que explican lo que se dice (o fotos del cliente), tras un storyboard aprobado por Gerard, con precapcut."
---

# Recursos (fase 2b de precapcut)

Se usa con un proyecto de CapCut ya cortado (fase 1) y con textos (fase 2). Herramienta:
`~/rmagency/AGENTES RM/herramientas/precapcut/` (flujo completo en `LEEME.md`). Trabajo en `~/rmagency/work/precapcut/<pieza>/`.

## Antes de nada
- Lee `aprendizajes/general.md` y `aprendizajes/<cliente>.md`. Reglas de Gerard que no se negocian:
  - **Sin texto** (el texto ya va en los titulares). Solo imagen o animación.
  - **Explicar, no rellenar**: pocos (3-5 por vídeo), concretos y reconocibles (objeto real o dibujo claro, nada de
    diagramas abstractos), ~2 s cada uno. **Nunca emojis ni iconos genéricos.**
  - Nunca tapan la cara, los titulares ni los subtítulos. Nada de keyframes de zoom que encojan el vídeo.
  - **Primero storyboard y OK de Gerard**; nunca se construye sin su OK.

## Pasos
1. `python3 precapcut.py recursos <pieza> "<proyecto>" --estilo <cliente> --solo-md --regenerar` y mira 5-6
   fotogramas pequeños de los momentos candidatos (ffmpeg `tile`) para ver qué se ve y dónde hay hueco.
2. Escribe un storyboard en `<pieza>/recursos-storyboard.md`: por recurso, tiempo, frase, qué muestra, cómo se
   anima y dónde va. Mándaselo a Gerard y espera su OK.
3. Con el OK: escribe `<pieza>/recursos.json` (`plantilla`, `ini`, `fin`, `t1`, `x_px`, `y_px`). Plantillas en
   `recursos/remotion/src/Explicativos.tsx` (rayado, color_cansa, puzle, muestrario, movil_foto, antes_despues,
   guardar, cajon…). Si hace falta una nueva, se añade ahí (SVG plano, marrón/blanco de la marca, sin texto).
   Con `--fotos <carpeta>` se pueden usar fotos del cliente (`"foto": ruta`).
4. QA antes de tocar CapCut: renderiza y compón 1 fotograma por recurso sobre el vídeo (alfa, sitio, que no tape).
5. CapCut cerrado (`pgrep -x CapCut`; si está abierto, pide a Gerard Cmd+Q, nunca lo cierres tú):
   `python3 precapcut.py recursos <pieza> "<proyecto>" --estilo <cliente>`. Copia de seguridad automática; los
   recursos se guardan DENTRO del proyecto (CapCut en Mac no lee fuera). `capcut lint` sin `--fix`.
6. Avisa a Gerard: lista de recursos con tiempo y qué hace cada uno.
