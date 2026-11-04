# Aprendizajes generales (todos los clientes)

## 2026-10-30 · Gerard (prueba Jesús Mora)
- Cortes: la base de cada clip es el vídeo original entero (hay que poder alargar en CapCut).
- No cortar a media sílaba: los bordes se miden con el audio, no solo con Whisper.
- Proyecto retocado a mano = solo se AÑADEN pistas; nunca se rehace el montaje encima.
- Subtítulos (los blancos): pista de subtítulos de CapCut de verdad (mover/cambiar uno cambia todos), como
  los automáticos de CapCut. Formato a copiar del proyecto de muestra de Gerard.
- Tipografía: siempre la de la marca, cargada como la carga CapCut (nunca la de sistema).
- Titulares: una palabra por línea; artículo/preposición + palabra juntos en la misma línea, el artículo en
  minúscula y más pequeño ("los RINCONES"). Cada línea entra cuando se dice; todas salen a la vez al acabar la idea.
- Titulares: mejor de más que de menos (Gerard borra los que sobran).
- Titulares: grandes, nunca cortados por el borde, todos en la misma zona: entre el primer y el segundo
  tercio (de mitad para arriba), que es donde va la vista y donde está el dinamismo.
- Exclamaciones / frases enfáticas ("por favor", "ojo", "nunca"...): muy grandes, negrita, centradas. Recurso
  preferido: rotoscopia (texto grande detrás del sujeto, tapado en parte pero legible, sin tapar la cara).
- Nada tapa la cara del sujeto principal.
- El sistema aprende: cada tip de un editor se apunta aquí (o en el del cliente).

## 2026-10-30 (tarde) · Gerard (revisión fase 2 v3)
- Subtítulos en formato subtítulo de CapCut: OK.
- Rotoscopia: OK, pero el texto grande tiene que verse ENTERO en pantalla (con margen, también al crecer).
  Se calcula con la fuente real: `PX_POR_UNIDAD` 5.5 (con 2.8 se salía mucho).
- Fuentes: CapCut (Mac) va en sandbox; una fuente local se referencia por su ruta dentro del contenedor
  (`~/Library/Containers/com.lemon.lvoverseas/Data/Library/Fonts/…`), sin resource_id (muestra «1030»).
- PENDIENTE (mejora): la ubicación de los titulares aún no está bien; de momento Gerard los coloca a mano.
  Cuando los deje bien, copiar sus posiciones/tamaños al estilo (sin tocar su proyecto).

## 2026-10-30 (noche) · Gerard (revisión fase 2 v4)
- La copia de la rotoscopia tiene que coincidir EXACTAMENTE con el clip de debajo (mismo encuadre, escala,
  posición, recorte) y estar MUDA. Si en CapCut se ve un sujeto más pequeño delante, es el recorte de CapCut.
- Ningún titular se sale de la pantalla: cada línea se mide con la fuente real y se encoge si no cabe.
- Los titulares no se tapan entre ellos: el alto de línea deja sitio a las tildes de las mayúsculas («VÍDEO»).
- Las negaciones (no, nunca, jamás, nada, ni, sin…) son importantes: siempre entran en el titular y en
  mayúsculas, como palabra clave («NO pongáis los típicos CUBERTEROS»).
- Si Gerard estira o mueve un clip, los textos se rehacen leyendo los tiempos reales del proyecto.

## 2026-10-30 (noche, 2) · Gerard
- Tamaños de titulares: perfectos (clave 36, menores 20, se encogen solo si no caben).
- Separación entre líneas de un titular: la de «guárdate / el VÍDEO» que dejó Gerard (justo para que la
  tilde no tape la línea de arriba): distancia entre centros = media de tamaños × 0.0056 (y de CapCut).
- Artículo + palabra («el VÍDEO»): el artículo en su propio texto, pegado a la palabra (en un mismo texto
  queda demasiado separado).

## 2026-10-31 · Gerard (fase 2b, recursos)
- Recursos según lo que se dice: motion graphics con el estilo de la marca (no hay pack: se hacen con
  Remotion); si se adjunta carpeta de fotos, se usan las fotos. Mejor de más que de menos.
- Nunca tapan la cara ni los titulares/subtítulos: van en el tercio de abajo, con fondo transparente.

## 2026-10-31 · Gerard (revisión recursos)
- Los recursos tienen que EXPLICAR lo que se dice: ilustraciones/diagramas hechos a medida del contenido y
  coherentes con lo que se ve en pantalla. Nada de emojis ni iconos genéricos («cutres»).
- Aquí NO vale «mejor de más»: pocos y con sentido (al revés que los titulares). Si no aportan entendimiento,
  no se ponen. Antes de construirlos: storyboard y OK de Gerard.

## 2026-10-31 (mañana) · Gerard
- Recursos SIN texto: solo imagen o animación (el texto ya va en los titulares). Como mucho una palabra si es
  imprescindible; mejor ninguna. («Guárdalo» del CTA: aprobado tal cual.)
- Nunca escalar ni mover el vídeo de forma que se vean bordes negros (keyframes de escala < 1 o desplazados).
  Si hace falta zoom: solo escala ≥ 1, centrada.
- La copia de la rotoscopia va SIEMPRE muda: clip a volumen 0 y además la pista silenciada; se comprueba en
  cada paso que escribe (`mudar_copias`).

## 2026-10-31 · espacio en disco (Gerard va justo)
- `montar` compila contra proxies negros mínimos (mismo nombre, tamaño y duración; `proxy_negro`) y luego
  apunta a los originales: capcut-cli ya no copia cientos de MB a assets/. Después `limpiar_assets`.
- Nunca `capcut lint --fix` en precapcut (copia medios a assets/ por «media-outside-draft»): lint sin --fix.

## 2026-11-01 · Gerard
- Fase 2b (recursos/gráficos) en pausa: este vídeo no servía para aprenderla. Se retoma más adelante con otro
  vídeo; lo aprendido hasta aquí (sin texto, que expliquen, objeto real, ~2 s) sigue valiendo.

## 2026-11-01 · Fase 3 sonidos (Gerard + coordinador)
- Solo efectos, sin música por ahora. Pop en la entrada de cada titular (uno por idea, no por línea); whoosh
  solo en cambios de plano reales (no en cada jump cut); impacto en exclamaciones; click en «Guárdalo».
- Sutiles: muy por debajo de la voz (QA: la mezcla mide lo mismo que la voz sola).

## 2026-11-01 (2) · Gerard (escucha de sonidos)
- Los efectos se tienen que OÍR: pops y efectos (impacto, click, check/error) a 0 dB en CapCut (volumen 1.0),
  no 17 dB por debajo. Los whoosh, ligeros (agudos, cortos) y a volumen bajo (0.14), como estaban.
- Nunca cortar la cola de un efecto: cada archivo acaba en silencio (fade) y se pone entero.
- Impacto = golpe grave con cola, reconocible; click = clic de ratón (pulsar + soltar).
- Si Gerard toca y pide «reinicia», se guarda su versión en backups/ y se vuelve a la nuestra.

## 2026-11-01 (3) · Gerard
- Efectos de sonido: los REALES de Mixkit (validados), no sintetizados. Se bajan con `sonidos/descargar.py`.
  Con los niveles pedidos (0 dB; whoosh 0.14), el impacto queda por debajo de la voz en los «POR FAVOR».

## 2026-11-03 · Gerard
- Biblioteca de sonidos = la de Gerard (19 sonidos de CapCut en «RM Dia de trabajo», Clip combinado16), ver
  `sonidos/biblioteca-gerard.md`. Él entrega los archivos en ese orden; hasta entonces van como `pendiente`.

## 2026-11-03 (2) · Gerard
- Librería de sonidos lista: sus 19 sonidos de CapCut (export de «Biblioteca sonidos RM» cortado con
  `sonidos-cortar`). Mixkit y sintetizados fuera de uso. Para elegir sonido, mirar `biblioteca-gerard.md`
  (cada uno tiene su para qué: idea, dinero, tensión, grillos = silencio incómodo, riser antes del CTA…).

## 2026-11-03 · Gerard (Aprenent fotografia, días 1 y 2, catalán)
- Los comentarios sueltos que pueden servir de gancho o para cortar el hilo NO se borran: van a la pista
  «Aparte», detrás del final del montaje, para que Gerard los coloque. En `decisiones.json`: `"aparte": true`
  (frase entera) o `"aparte_palabras": [k...]` (solo esas palabras). Las tomas repetidas sí se quitan.
- Gerard quiere el proyecto en CapCut, no un render: `montar --sin-preview` salta el preview (solo es para el QA).
- Preview con vídeos 4K: se renderiza por trozos (`-ss` antes de `-i`); el filter_complex único no acababa.
- Catalán: «em» es pronombre, no muletilla (ya no se quita si el idioma es `ca`).
- Whisper en catalán «oye» «Gràcies per acompanyar-nos», «i Vimeo», «xavi.com»… sobre habla real mal
  reconocida: no quitar esas palabras a ciegas, casi siempre debajo hay voz.
- Las fotos que acompañan al vídeo van en una pista «Fotos» (3 s cada una) detrás de «Aparte».

## 2026-11-03 (3) · Gerard
- Risers (18 `riser`, 16 `riser-corto`): para la tensión inicial / intriga, sobre todo cuando se hace una
  pregunta; el riser acaba justo cuando acaba la pregunta (empieza la respuesta). 1-2 por vídeo como mucho.
- Los nombres de los sonidos son genéricos por papel (cuándo usarlos), nunca por el vídeo de muestra.

## 2026-11-03 (4) · Gerard
- Fase 3 con su librería: «mucho mejor». Se da por buena la configuración actual (pops/efectos 0 dB, whoosh y
  transiciones bajos, riser en preguntas).

## 2026-11-03 (mediodía) · Gerard (Aprenent fotografia, fase 2)
- Gerard monta cada día en un clip combinado (materials.drafts[].draft) y apila los ganchos (versiones de Trial
  Reels) en pistas encima, al principio. Las fotos van DENTRO del combinado, en el momento en que presenta cada una.
- Subtítulos: re-transcribir el audio del montaje FINAL con contexto (faster-whisper medium, vad, condition_on_previous_text,
  prompt con vocabulario): mucho más limpio que la transcripción de fase 1 (hecha sin contexto para ver tomas).
  Una pista de subtítulos para la narración y una por gancho («Subtitulos ganxo dia N-k»).
- `sync-timelines --nested --apply` reconcilia desde draft_content.json: sincronizar antes de que draft_content quede viejo.

## 2026-11-03 · prueba completa con Crudo.MOV (Jesús)
- Whisper se equivoca de toma: pone las palabras de la buena en un intento murmurado. Si una frase buena
  llega sin su principio, re-transcribir la ventana y añadir las palabras con `"anadir"` en decisiones.json.
- Tomas susurradas o ensayos en voz baja (~25 dB por debajo de la voz normal) no sirven aunque Whisper las
  transcriba bien: comprobar el nivel antes de elegirlas.
- Pausas de duda dentro de una frase («No… es… lo mismo»): se cortan por energía, pero solo donde no hay una
  palabra de duración normal (la voz baja también queda bajo el umbral). Arranques en falso dentro de la frase
  («No…» y vuelve a empezar) se quitan a mano con `quitar_palabras`.
- Charla con el cámara pegada al guion («tú todo el rato vas grabando…»): fuera con `quitar_palabras`.
- (03/11, tarde) Gerard: los subtítulos van DENTRO de cada clip combinado (uno por gancho también), y cada combinado
  se recorta al final de su vídeo principal (nada de negro al final). Hecho con `scripts-sueltos/` (aún no en precapcut.py):
  `retrans.py` (audio de cada pista del combinado → texto), `dentro.py` (capcut caption en un proyecto temporal SIN textos,
  si no `caption` añade a la pista de mismo nombre) y `trasplante.py` (mete pistas+materiales en materials.drafts[].draft
  de todas las copias, incluidas subdraft/*, y ajusta duraciones arriba).

## 2026-11-03 · fase 2 con Crudo (Jesús)
- Planos abiertos: la cara cae en la zona de titulares (1.er–2.º tercio). Si no cabe de lado sin salirse de la
  pantalla, el titular sube encima de la cabeza (`y_arriba`), nunca encima de la cara ni abajo (subtítulos).
- Cada titular se ve al menos 0,8 s: el siguiente espera (si no, «NO es lo MISMO» se perdía).
- Correcciones de varias palabras en subtitulos.json («y doyles» → «duele», «al mundo» → «al»); las palabras
  añadidas con «anadir» en fase 1 también llegan a los subtítulos.

## 2026-11-03 · recursos con Crudo (Gerard aprueba el storyboard entero)
- Recursos sin texto aprobados: raya en encimera («delicados»), muestra de color que se apaga («cansan»), pieza
  de puzle que rebota en una casa («no encajan»), muestrario en abanico («texturas, colores, acabados»), móvil
  con foto que sale de la pantalla («foto vs delante»). Plantillas: rayado, color_cansa, puzle, muestrario, movil_foto.
- En planos abiertos con el sujeto en el centro: pequeños en las esquinas de abajo, alternando lado.
- Los recursos apuntan a su render en <pieza>/recursos/ (no se copian dentro del proyecto).

## 2026-11-04 · Gerard («se ha perdido la ruta de los gráficos»)
- CapCut (Mac, sandbox) no lee ~/rmagency: los recursos renderizados van DENTRO del proyecto
  (`<proyecto>/precapcut-recursos/`). Los vídeos grandes siguen fuera (en el disco o ~/Movies).
- (04/11) Versiones para Trial Reels: Gerard pide varias versiones por capítulo, una por gancho y cada una más corta,
  como clips combinados NUEVOS copiados de los suyos (los originales no se tocan). `scripts-sueltos/versiones.py`:
  copia el combinado con ids nuevos (+ carpeta subdraft), deja visible solo el gancho elegido y sus textos y hace
  cortes en onda (ripple) en todas las pistas; un texto con la mitad dentro del corte se quita entero.

## 2026-11-04 · sonidos con Crudo
- El nivel de los efectos depende de la voz de cada vídeo: se toma la relación que aprobó Gerard en Jesús
  26-10 (sus sonidos a 0 dB → efectos ~4 LU por encima de la voz, medido en mono) y se escala para que se
  mantenga (`nivel_efectos`). Crudo tiene la voz muy baja (-26 LUFS) → efectos x0,26.
- Cada recurso con su sonido: rayado → marcar, puzle → error, muestrario → chasquido, móvil → sorpresa.
- Los sonidos los copia capcut-cli dentro del proyecto (assets/): CapCut los lee.

## 2026-11-04 · Gerard: OK a la prueba completa con Crudo (cortes → textos → recursos → sonidos)
- Primer vídeo hecho de punta a punta con precapcut y aprobado. La configuración actual es la referencia.
- (04/11, corrección de Gerard) En cada versión: UN solo gancho, integrado en la pista principal al principio (no
  encima), y el vídeo justo detrás sin hueco negro. El arranque del vídeo («Bé, un altre cop estem per aquí») también
  cuenta como gancho: fuera en las demás versiones y con versión propia.
- (04/11) Música: Gerard deja la canción al final de la pista principal con su velocidad y volumen; se copia DENTRO de
  cada versión a su duración (mismo inicio, velocidad, volumen) + fundido de salida 1,5 s (`audio_fades`).
- (04/11) Títulos de capítulo («DIA N / APRENENT FOTOGRAFIA»): como textos sueltos (type "text", no subtítulo) en cada
  versión, copiando la composición del clip combinado del título; sirven de título y portada del reel.
  `scripts-sueltos/musica_titulos.py`.

## 2026-11-04 · referencia que pasó Gerard (vídeo «Motion graphics con un solo prompt», Remotion + Claude)
- Método del vídeo: 1) un prompt que genera un «súper prompt» a partir de la web/marca del cliente; 2) ese súper
  prompt a Claude Code con las skills de Remotion; 3) correcciones (más tiempo de lectura, motion blur, entradas
  con blur, que la música no acabe cortada) y adaptar formato (vertical/cuadrado).
- Ideas aplicables a la fase 2b (pendiente de que Gerard diga cuáles): brief visual por cliente a partir de su
  web + kit de marca; skills oficiales de Remotion; motion blur y transiciones más finas en las plantillas.
- (04/11) Música: cuando Gerard ajusta una versión «para que pongas como esa todas», copiar de esa versión velocidad Y
  volumen (y el resto de ajustes del clip de audio). No dar por hecho que la velocidad se queda igual.

## 2026-11-04 · Gerard: recursos en 3D (skills oficiales de Remotion)
- Las animaciones 2D planas se veían «sosillas». Aprobado: recursos en 3D (Three.js con `@remotion/three`):
  volumen, luz de estudio y materiales reales (mármol, madera con veta, lacado del color de la marca), sin texto
  y sin tarjeta de fondo. Plantillas `*_3d` en `recursos/remotion/src/Explicativos3D.tsx`; las nuevas, igual.
- Entran enfocándose desde blur y salen desenfocándose; motion blur (`CameraMotionBlur`) solo en el render final.
- Más tiempo de lectura: cada recurso dura 1,8–3 s (antes 1,2–2,6) si hay hueco hasta el siguiente.
- Sin tarjeta, que no se peguen a la cara ni a las manos del que habla (mover `x_px`/`y_px`).
- (04/11) ERROR mío: cortes en onda con tiempos redondeados a centésimas dejaron restos de 1 fotograma y un hueco en la
  pista principal (Gerard: «clips de mierda de 0,01 s»). Los cortes se ajustan SIEMPRE a los bordes reales de los clips
  (o a fotograma, 1/30 s) y después se comprueba: ningún clip < 0,1 s ni hueco en la principal (`limpiar_restos.py`).

## 2026-11-04 · Gerard (fallos de cortes en «Aprenent fotografia»)
- Cortes en microsegundos enteros y en fotogramas exactos (con segundos a 2 decimales quedaban restos de 1
  fotograma y huecos negros). Reglas completas y QA obligatoria en LEEME («Cortes en fotogramas y QA»).
- Antes de entregar cualquier versión: `qa-capcut`. Con un fallo no se entrega.
