# precapcut: vídeos medio editados en CapCut, por fases

Deja el proyecto de CapCut medio hecho para que Gerard (o Andrea o Jaume) le dé el toque final.
Se revisa **después de cada fase**: los subtítulos y los sonidos se montan sobre cortes ya aprobados,
así no se descuadran.

| Fase | Qué hace | Estado |
|---|---|---|
| 1 · Cortes | Transcribe en local con tiempos por palabra, quita tomas falladas, arranques en falso, muletillas y silencios, y lo monta en CapCut | **hecha** |
| 2 · Subtítulos | 1-2 palabras por bloque desde la misma transcripción + titular (palabra clave grande) por frase, estilo por cliente en `estilos/` | **hecha** (prueba Jesús Mora 30/10) |
| 2b · Recursos | Motion graphics (Remotion, estilo de marca, fondo transparente) según lo que se dice; fotos si se adjunta carpeta | **hecha** (prueba Jesús 31/10) |
| 3 · Sonido | Librería RM de efectos (Mixkit/Pixabay) colocados según el contenido | pendiente |
| 4 · Humano | Lo creativo, en CapCut | — |

## Cómo se pide

«Pre-edita los vídeos C0038 a C0041 de `<carpeta>` en el proyecto de CapCut «X»». Claude sigue esto:

1. `python3 precapcut.py fase1 <pieza> <vídeos en orden de grabación> [--idioma es|ca]`
   - `<pieza>` = nombre corto sin espacios (p. ej. `jesus-2026-10-26`). Todo queda en
     `~/rmagency/work/precapcut/<pieza>/`.
2. **Leer solo `fase1.md`** (tabla de frases ✓/✗). Nunca abrir el vídeo ni `transcripciones.json`.
   Revisar con criterio lo que el script no ve:
   - Si dos frases dicen lo mismo con otras palabras, quedarse con la mejor (normalmente la última).
   - Frases sueltas fuera del guion («¿grabas?», «vale, otra vez», «corta») → fuera.
   - Para cambiar algo, editar `decisiones.json` (`queda`: true/false) con un script corto y poner
     `"a_mano": true` en esa frase: así no se pierde si se vuelve a lanzar `fase1`. `montar` reescribe
     `fase1.md` con las decisiones finales.
3. `python3 precapcut.py montar <pieza> --en "<proyecto CapCut vacío>"` (o `--nuevo "<nombre>"`).
   **CapCut tiene que estar cerrado.** Hace copia del proyecto en `<pieza>/backups/` antes de escribir.
   Volver a montar sobre el mismo proyecto (el que ya llenó precapcut) lo vacía y lo rellena;
   un proyecto de Gerard con el mismo nombre no se toca nunca.
   Deja también `preview.mp4` (baja resolución) y `edl.csv`.
4. `python3 precapcut.py qa <pieza>` → re-transcribe el preview y lista palabras comidas o sobrantes
   (`qa-fase1.md`), y mide el audio en cada borde: «corte entra/sale con sonido» = sílaba comida
   (re-transcribir no lo ve: "-sí" se sigue leyendo "así"). Revisar las que caen en un borde de corte. Regla de Gerard: **no se presenta
   nada sin QA propio** (silencios, frases a medias, cortes a mitad de palabra).
5. Avisar a Gerard: duración bruto → montado, cuántas tomas fuera, frases dudosas, y que abra el
   proyecto en CapCut. **Esperar su OK antes de la fase 2.**

## Antes de cada fase: aprendizajes

Leer `aprendizajes/general.md` y `aprendizajes/<cliente>.md`. Cada tip nuevo de Gerard, Andrea o Jaume se
apunta ahí (con fecha y autor, sin borrar nada) y, si es medible, también en `estilos/<cliente>.json`.

## Fase 2 · Subtítulos

1. Estilo del cliente en `estilos/<cliente>.json` (ver `estilos/LEEME.md`). Si no existe: sacarlo del vídeo
   de referencia (hoja de 24 fotogramas pequeños con ffmpeg `tile`) + kit de marca, bajar las fuentes
   (Google Fonts, OFL) a `fuentes/` (los instaladores las ponen en las fuentes del usuario) y, cuando
   Gerard retoque textos en CapCut, copiar sus valores con `capcut make-preset` (es la referencia buena).
2. `python3 precapcut.py subtitulos <pieza> "<proyecto>" --estilo <cliente> --solo-md` → leer **solo**
   `subtitulos.md` y escribir en `<pieza>/subtitulos.json`: `"correcciones"` (lo que el reconocedor escribe
   mal) y `"claves"`: por frase, la lista de palabras que llevan titular (`{"F005": ["rincones", "riñonero",
   "hueco"]}`; `""` = ninguno). **Mejor de más que de menos**: Gerard borra los que sobran.
3. Sin `--solo-md` (CapCut cerrado): lee los cortes REALES del proyecto y AÑADE (nunca toca el vídeo):
   - `Subtitulos`: subtítulos de CapCut de verdad (formato copiado de los automáticos: material
     `type: subtitle` + `words`, un `group_id` común —lo que hace que cambiar uno cambie todos— y pista
     `flag` 1). Se crean con `capcut caption --words` y se convierten (`a_formato_subtitulo`).
   - `Titulares 1..n`: una línea por palabra (artículo/preposición + palabra juntos: «los RINCONES», el
     artículo en pequeño); cada línea **entra cuando se dice** y **todas salen a la vez** al acabar la
     idea. Todos en la misma zona (entre el 1.er y el 2.º tercio), centrados, grandes; el ancho se mide con
     la fuente real y solo se encogen si no caben. Separación entre líneas = media de tamaños ×
     `SEPARACION_LINEAS` (referencia de Gerard «guárdate / el VÍDEO»); el artículo va en su propio texto
     (`Titulares N articulo`) pegado a la palabra. Si taparían una cara (OpenCV) se mueven de lado.
   - `Exclamaciones` («por favor», «ojo», «nunca»… lista en el estilo): texto enorme centrado, crece un poco,
     y **rotoscopia**: copia del clip recortada a la exclamación, muda, con quitar fondo (`matting`) y por
     encima del texto (render_index 16000), así el sujeto queda delante.
   - Jesús: si se nombra un color («nogal oscuro», «gris») esas palabras salen en ese color (`colores`).
   `--rehacer` quita solo lo de precapcut (pistas con esos nombres y las `-copy`) y lo vuelve a poner;
   lo que Gerard añada a mano no se toca. **Fuentes** (`fijar_fuentes`): en Mac CapCut va en sandbox y busca
   las fuentes instaladas en su contenedor (`~/Library/Containers/com.lemon.lvoverseas/Data/Library/Fonts/`);
   se escribe esa ruta (formato copiado del proyecto de muestra «1030»). CapCut 9.5 guarda los proyectos
   nuevos en `Projects/CapCut Drafts/` (`buscar_proyecto` mira las dos carpetas).
4. QA: `capcut lint` («caption-too-fast» es normal palabra a palabra) + 5 fotogramas con el texto dibujado
   (render `capcut render --scale 0.5` + `drawtext` con las fuentes): legible, ninguna cara tapada, bien
   escrito, titulares escalonados. Los bloques arrancan con el sonido (Whisper da los inicios ~90 ms tarde).
5. Avisar a Gerard y esperar su OK antes de la fase 3.

## Fase 2b · Recursos

1. `python3 precapcut.py recursos <pieza> "<proyecto>" --estilo <cliente> [--fotos <carpeta>] --solo-md --regenerar`
   → leer **solo** `recursos.md`. Propone un recurso por idea (clave de cada titular) + números (contador),
   negaciones (cruz) y «aquí» (flecha), sin solaparse. Revisar con criterio y editar `recursos.json`:
   `plantilla` — explicativas (las buenas): `cajon` (bandeja estándar con huecos → madera a medida; t1 = madera, t2 = se estira), `cajon_orden` (se llena de cubiertos ordenados), `esquina` (planta en L con rincón perdido), `rinonero` (bandejas que salen girando; t1 = rincón aprovechado), `guardar` (botón de guardar de Instagram), `antes_despues` (dos mitades, ~2 s; t1 = aparece la buena), `etiqueta` («PALABRA = explicación» sobre el objeto real), `zoom` (no se renderiza: keyframes de escala/posición en el clip de debajo, `escala`, `x`, `y`; también en la copia de rotoscopia si coincide); `x_px`/`y_px` por recurso para esquivar la cara; genéricas solo si explican algo: carpeta · contador · check · cruz · lista · flecha (`icono` con emoji: NO, Gerard 31/10), `texto`, `icono` (emoji),
   `items`, `numero`, o `foto` (ruta; con `--fotos` sale `fotos-hoja.jpg` para elegir por contenido).
   Primero storyboard (qué explica cada uno, cómo, dónde) y OK de Gerard; pocos y que expliquen (ver aprendizajes). Las ilustraciones nuevas se añaden a `recursos/remotion/src/Explicativos.tsx`.
2. Sin `--solo-md` (CapCut cerrado; sin `--regenerar` respeta `recursos.json`): renderiza cada uno con
   Remotion (`recursos/remotion`, ~3 s cada uno; ProRes 4444 con alfa, 1080x1920, el elemento en el tercio
   de abajo: `estilos/<cliente>.json` → `recursos.y_px`) y los AÑADE en la pista `Recursos` (rehacer = solo
   esa pista). `recursos/remotion/node_modules` es un enlace a `proyectos/remotion-video/node_modules`
   (en otro ordenador: `npm i` dentro de `recursos/remotion`).
3. QA: fotogramas con el recurso encima (alfa, sitio, que no tape cara ni subtítulos) y `capcut lint`.

## Reglas

- **Si Gerard ya ha tocado el proyecto en CapCut, no se vuelve a `montar` encima** (lo vaciaría).
  Las fases 2-3 solo AÑADEN pistas, leyendo los tiempos reales con `capcut segments
  "<proyecto>/draft_info.json"` (CapCut 9.5 guarda ahí; `draft_content.json` se queda en lo que escribió
  precapcut). Para mejorar la herramienta: `montar --sin-capcut` y comparar `edl.csv`.

- Coste: el modelo solo lee `fase1.md` / `qa-fase1.md`. Transcripción, cortes y render son locales.
- No se sube audio a ningún servicio (nada de `capcut caption --cloud`).
- CapCut congelado en la **9.5**: la 10 rechaza los proyectos escritos por capcut-cli.
- Si una palabra sale mal siempre (nombres, marcas), añadirla a `vocabulario.txt`.

## Clips que se puedan alargar (ffprobe)

capcut-cli necesita **ffprobe** para saber cuánto dura cada vídeo; sin él, el material de CapCut acaba
donde acaba el corte y no se puede alargar ningún clip. `precapcut.py` lo resuelve solo: usa el ffprobe del
PATH y, si no hay (este Mac), `ffprobe_pyav.py` (el ffprobe de static-ffmpeg no lee los MP4 de la Sony).
En Windows hace falta ffmpeg instalado (`winget install Gyan.FFmpeg`).
Para un proyecto ya montado sin esto (o tocado a mano): con CapCut cerrado,
`python3 precapcut.py materiales <pieza> "<proyecto CapCut>"` → cada clip pasa al vídeo original entero sin
mover ningún corte (copia en `backups/`, sincroniza `Timelines/`). Lo que de verdad limita alargar es la
lista del panel de medios de `draft_meta_info.json`, que capcut-cli no toca: `apuntar_originales()` (dentro
de `montar` y de `materiales`) pone ruta original y duración entera ahí y en todas las copias del timeline. El material queda apuntando al original
del disco: el disco tiene que estar conectado para abrir el proyecto.

## Instalar en otro ordenador

- Mac: `bash instalar-mac.sh` · Windows: `instalar-windows.ps1`. Instala capcut-cli, faster-whisper
  y el modelo `medium` (~1,5 GB la primera vez).
- La carpeta de proyectos de CapCut se detecta sola (Mac: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`,
  Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`).

## Ajustes (arriba de `precapcut.py`)

`PAD_ANTES` 0,08 s y `PAD_DESPUES` 0,15 s de margen alrededor de cada palabra, y además el corte se
lleva hasta donde empieza/acaba el sonido (`BUSCA_ANTES` 0,6 s / `BUSCA_DESPUES` 0,4 s), porque
Whisper da los inicios tarde; una palabra de más de `PALABRA_MAX` 1,5 s se re-transcribe sola (Whisper
sin VAD a veces se traga una toma entera dentro de una palabra); `PAUSA_MAX` 0,35 s de
pausa permitida dentro de una frase; `SIM_TOMA` 0,6 de parecido para dar una frase por repetida.
