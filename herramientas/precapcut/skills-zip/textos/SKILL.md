---
name: "textos"
description: "Fase 2 de pre-edición en CapCut: añade subtítulos palabra a palabra, titulares escalonados y rotoscopias de exclamaciones al proyecto ya cortado, con el estilo del cliente (precapcut)."
---

# Textos (fase 2 de precapcut)

Añade al proyecto de CapCut, ya cortado y aprobado en la fase 1 («cortes»), tres cosas:
- los subtítulos palabra a palabra, en formato de subtítulos de CapCut;
- los titulares;
- las exclamaciones con rotoscopia.

Solo **añade pistas**: no toca nunca los cortes. Gerard revisa antes de pasar a la siguiente fase.

## Antes de empezar

- Herramienta: `~/rmagency/AGENTES RM/herramientas/precapcut/` en el Mac de Gerard, o `herramientas/precapcut/` del repo `rmagencyproyectos/rm-agentes` en otros ordenadores.
- **Lee siempre `aprendizajes/general.md` y `aprendizajes/<cliente>.md`.** Ahí están las reglas que han ido dando Gerard y los editores.
- Estilo del cliente: `estilos/<cliente>.json`. Si el cliente no tiene, créalo a partir de un vídeo editado y de su kit de marca (fuentes, colores, tamaños, sombras), y pide a Gerard que retoque los primeros textos para tomarlos como referencia.
- Las fuentes tienen que estar en `fuentes/`. En Mac, CapCut solo las encuentra dentro de su propia carpeta, y la herramienta ya las apunta ahí.

## Pasos

1. `python3 precapcut.py subtitulos <pieza> "<proyecto>" --estilo <cliente> --solo-md`. Lee **solo** `~/rmagency/work/precapcut/<pieza>/subtitulos.md` (titulares, exclamaciones y subtítulos). No leas nunca el JSON del proyecto.
2. Revisa con criterio y corrige en `<pieza>/subtitulos.json`, en `{"correcciones": {"mal": "bien"}, "claves": {"F005": ["rincones"], "F009": ""}}`:
   - faltas de transcripción y nombres propios (que además van a `vocabulario.txt`);
   - palabras clave de cada titular;
   - **las negaciones (no, nunca, jamás, nada, ni, sin) van siempre en el titular y resaltadas**.
3. Comprueba que CapCut está **cerrado** (`pgrep -x CapCut`). Si está abierto, pide a Gerard que lo cierre y no lo mates nunca. Luego ejecuta `python3 precapcut.py subtitulos <pieza> "<proyecto>" --estilo <cliente>`. Añade `--rehacer` para sustituir los textos que puso precapcut antes. La herramienta hace copia de seguridad y lee los tiempos reales del proyecto, por si Gerard ha alargado algún clip.
4. QA propio, que es obligatorio:
   - `capcut lint "<proyecto>/draft_info.json"`. Los avisos de caption-too-fast son normales.
   - Render de baja resolución con los textos dibujados. Revisa algunos fotogramas: que nada tape la cara, que ningún titular se salga de pantalla, que no se pisen las líneas (las tildes incluidas) y que no haya faltas.
   - Comprueba que las copias de rotoscopia tienen volumen 0 y el mismo encuadre que el clip base.
5. Avisa a Gerard en pocas líneas: número de subtítulos, titulares y exclamaciones, y lo que debe revisar en CapCut (la rotoscopia solo se ve allí). **Espera su OK.**

## Reglas de estilo (base de Gerard; los detalles están en aprendizajes)

- **Subtítulos.** Van en la pista de subtítulos de CapCut, en un mismo grupo, para que al cambiar uno cambien todos. Una o dos palabras cada vez.
- **Titulares.**
  - Una palabra por línea; el artículo o la preposición va en un texto aparte, pegado a su nombre («el VÍDEO»).
  - Palabras menores en minúscula y más pequeñas; la palabra clave en mayúscula.
  - Cada línea entra cuando se dice y todas salen a la vez al acabar la idea.
  - Todos en la misma zona, entre el primer y el segundo tercio del encuadre. Ninguno tapa la cara, ninguno se sale de pantalla y no se pisan.
  - **Mejor muchos que pocos**: Gerard borra los que sobran.
- **Exclamaciones** («por favor», «ojo», «nunca»…). Van enormes, en negrita y centradas, con rotoscopia: la copia del clip lleva el fondo quitado y va por encima, el texto va entre las dos capas y la copia está **muda**. El texto entra entero en pantalla.
- Las reglas de cada cliente están en su archivo de aprendizajes. Por ejemplo, para Jesús Mora: cuando se nombra un color, esas palabras van en ese color.

## Cuando Gerard o un editor da un consejo nuevo

Añádelo a `aprendizajes/general.md` o a `aprendizajes/<cliente>.md`, con fecha y autor. Si se puede medir (tamaños, distancias, colores), pásalo también a `estilos/<cliente>.json`. Si sirve para otros, súbelo a git.