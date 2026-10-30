# Estilos de subtítulos (fase 2)

Un `.json` por cliente (`<slug>.json`, el mismo slug que `memoria/clientes/`). Lo lee
`precapcut.py subtitulos <pieza> "<proyecto>" --estilo <slug>`. Los valores buenos salen de los textos
que Gerard retoca a mano en CapCut (`capcut make-preset <proyecto> <id> --out x.json`).

- `subtitulos`: los blancos que siguen a la voz. `palabras_por_bloque` 1-2 (nunca se parte una palabra),
  `mayusculas`, `color`, `tamano` (unidades de CapCut), `negrita`, `x`/`y` (-1…1, centro 0, y positiva =
  arriba), `sombra` {color, alpha, distancia, difuminado, angulo}, `borde`.
- `titular` (o `null`): `clave` (la palabra importante, en mayúsculas) y `menor` (el resto y los artículos,
  en minúsculas y pequeño), cada uno con fuente/tamaño/color/sombra/`espaciado`; `x`, `y` (arriba del
  bloque), `y_alternativa` (adonde se baja si taparía una cara), `hueco` entre líneas, `palabras_antes`
  (cuántas palabras de antes de la clave entran), `salida_extra` (s que se queda tras acabar la idea).
- `colores_nombrados` + `colores` {nombre: #hex}: las palabras que nombran un color salen en ese color.
- `archivo_fuente`: el .ttf, relativo a la carpeta de precapcut (`fuentes/`).
- `fuente_evidencia`: de dónde sale el estilo, para poder revisarlo.
