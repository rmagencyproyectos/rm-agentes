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
