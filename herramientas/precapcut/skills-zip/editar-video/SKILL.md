---
name: "editar-video"
description: "Punto de entrada para editar o pre-editar un vídeo de un cliente de RM Agency en CapCut con precapcut: pregunta el cliente, revisa o da de alta su kit de marca y lleva a la editora fase a fase (cortes, textos, recursos, sonidos) con revisión entre una y otra. Úsala cuando alguien diga «quiero editar un vídeo», «pre-edita estos vídeos» o similar."
---

# Editar un vídeo con precapcut (punto de entrada)

Herramienta: `~/rmagency/AGENTES RM/herramientas/precapcut/` (todo el detalle en `LEEME.md`). Quien te habla puede
no saber nada de la herramienta: guíala paso a paso, en castellano llano, sin comandos ni tecnicismos.

## 1. Arranque
- Ejecuta `python3 precapcut.py empezar` y resume a la editora los pasos en 4-5 líneas.
- Lee `aprendizajes/general.md` (reglas de Gerard y de los editores; mandan sobre lo que creas tú).

## 2. Cliente y kit de marca
- Pregunta de qué cliente es el vídeo. `python3 precapcut.py clientes` lista los que hay.
- Cliente existente: `python3 precapcut.py cliente <slug>`. Si todo es ✓, lee `aprendizajes/<slug>.md` y sigue.
- Cliente nuevo o con ✗: pide su kit de marca: fuentes (archivos o nombres de Google Fonts), colores en #hex, logo
  y, si hay, un vídeo de referencia o un proyecto de CapCut con textos retocados a mano.
  - `python3 precapcut.py nuevo-cliente <slug> [--kit <carpeta>] [--google "Fuente1" "Fuente2"]`.
  - Rellena `estilos/<slug>.json` donde pone COMPLETAR: fuentes y colores del kit; tamaños y posiciones de partida
    los de jesus-mora; si hay proyecto retocado, copia sus valores (`capcut make-preset <proyecto> <id>`); si hay
    vídeo de referencia, míralo en una hoja de 24 fotogramas pequeños (ffmpeg `tile`) y anota su estilo.
  - Pon en `fuente_evidencia` de dónde sale cada cosa. Repite `cliente <slug>` hasta que todo sea ✓.
- La fase 1 (cortes) no necesita el kit: se puede empezar mientras se completa.

## 3. Vídeos
Pregunta dónde están los brutos y en qué orden se grabaron. Elige un nombre de pieza corto
(`<cliente>-<fecha>`) y un nombre de proyecto de CapCut nuevo (nunca uno existente de Gerard o de la editora).

## 4. Fases, en orden, con revisión después de cada una
Usa la skill de cada fase: **cortes** → **textos** → **recursos** → **sonidos**.
- Antes de cualquier escritura en CapCut: `pgrep -x CapCut`. Si está abierto, pide a la editora que lo cierre con
  Cmd+Q y espera su «listo»; nunca lo cierres tú.
- Al acabar cada fase: dile qué has hecho (corto), qué mirar en CapCut y espera su «ok» o sus cambios.
- Si ha tocado el proyecto a mano: solo se añade encima, nunca se rehace.

## 5. Aprender
Cada tip o corrección de la editora se apunta al final de `aprendizajes/general.md` (o `aprendizajes/<slug>.md` si
es del cliente) con fecha y autora, sin borrar nada; si es medible (tamaño, color, posición, volumen), también en
`estilos/<slug>.json`. Díselo: «apuntado para la próxima».
