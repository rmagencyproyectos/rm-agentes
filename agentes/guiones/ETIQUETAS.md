# Las etiquetas de una pieza — qué va en cada columna

> **Fuente única.** Reordenado el 02/10/2026 por petición de Gerard: las cuatro columnas se
> solapaban (Humor, Caso real, Receta, Día de trabajo y Predicción estaban en dos columnas a la
> vez), así que la misma cosa cabía en dos sitios y cada uno la ponía donde le parecía. Sin
> fronteras claras, lo que se mide no significa nada.
>
> Las listas de aquí son **cerradas**. Para añadir una opción: se añade AQUÍ primero, con su
> definición, y luego se siembra en Notion con `infra/notion/etiquetas_idea.py`.

## La regla: cada columna responde una pregunta distinta

| Columna | Pregunta | Cuántas por pieza |
|---|---|---|
| **Tipo de idea** | ¿De qué va? (el asunto) | 1, a veces 2 |
| **Formato** | ¿Qué forma tiene por fuera? | 1, a veces 2 |
| **Plantilla** | ¿Cómo se escribe el guion? (la mecánica) | **1** |
| **Palanca** | ¿Por qué se queda el espectador? | 1-2 |

Si una etiqueta encaja en dos columnas, **está mal definida**: mira la tabla de desempates
del final.

---

## Tipo de idea — ¿de qué va?

El asunto de la pieza. Responde "este vídeo habla de…".

| Opción | Es esto | No es esto |
|---|---|---|
| `Producto` | El producto o servicio es el protagonista | Si solo sale de fondo mientras se explica un oficio → `Oficio` |
| `Oficio` | El saber hacer: cómo se hace, con qué, por qué así. Incluye los secretos, los materiales y las medidas | Si es la jornada entera sin enseñar criterio → `Día de trabajo` |
| `Día de trabajo` | La jornada, el sitio, la gente trabajando. Lo que no se ve de dentro | Si se enseña una técnica concreta → `Oficio` |
| `Cliente` | Un encargo, un caso, un testimonio, una reacción real | Si el cliente es un ejemplo inventado → el tipo que toque |
| `Local y zona` | El sitio, una apertura, un evento, la ciudad | Nombrar la ciudad **no** basta para marcar esto: eso es una regla de todas las piezas (ver `_comun.md`) |
| `Opinión` | El profesional se moja sobre algo discutible del sector | Explicar cómo funciona algo no es opinar → `Oficio` |
| `Humor` | La pieza existe para hacer gracia | Si hace gracia pero va de un producto, y el chiste es secundario → `Producto` |
| `Interactiva` | Le pide algo al espectador: elegir, votar, acertar, responder | Un CTA al final no convierte la pieza en interactiva |

> **`Oficio` no lo pone el etiquetado automático** (Gerard, 02/10/2026). En clientes que enseñan
> su propio trabajo (un entrenador, un carpintero) saldría en casi todo y no distingue nada.
> Una lección o un tip sin más ángulo va con Tipo de idea **vacío**: de qué trata en concreto lo
> dicen el Formato y las **Etiquetas del cliente**. Sigue en la lista para ponerlo a mano.

## Formato — ¿qué forma tiene?

Cómo está armada por fuera. Es lo que reconoces sin oír el audio.

| Opción | Es esto |
|---|---|
| `Lista / Top` | Varios elementos enumerados, con o sin orden (absorbe lo que antes era Ranking, Top 10 y Lista) |
| `Tips` | Consejos aplicables, sin ranking |
| `Comparación` | Dos o más cosas enfrentadas: A vs B, bueno vs malo |
| `Paso a paso` | Instrucciones para reproducirlo: cantidades, orden, medidas (antes `Receta`) |
| `Proceso` | De principio a fin, se ve la transformación. **No** da instrucciones |
| `Explicación` | Alguien explica a cámara, argumentando |
| `Reto al espectador` | Pregunta, votación o reto dirigido a quien mira |
| `A pie de calle` | Con gente de fuera, en la calle |
| `Trend` | Monta sobre un audio o formato de moda (antes también `Tendencia`) |
| `Producto en primer plano` | Plano corto del producto, textura, detalle (antes `Foodporn`) |
| `Vlog / Crónica de evento` | Se acompaña al equipo en un evento, visita o salida y se cuenta lo que pasa (añadido el 03/10/2026: Gemini lo pedía en 5 vídeos de Golossa y 1 de NewMos) |
| `Tomas falsas / Bloopers` | Errores, risas y momentos sin guion del equipo (añadido el 03/10/2026) |
| `Sketch` | Escena de humor con guion, interpretada por el equipo (añadido el 04/10/2026: Gemini lo pedía en 13 vídeos de Golossa) |

## Plantilla — ¿cómo se escribe?

La mecánica del guion. **La lista no vive en Notion: es la carpeta
`agentes/guiones/plantillas/`** — un archivo, una plantilla, con su gancho, sus beats y su
evidencia. Catálogo y estado: `plantillas/README.md`.

**Una sola por pieza.** Si crees que lleva dos, elige la que manda en el gancho.

## Palanca — ¿por qué se queda?

El resorte. Lo que hace que no deslice.

`Curiosidad` · `Problema` · `Deseo` · `Identificación` · `Sorpresa` · `Debate` · `Predicción`

| Opción | Es esto |
|---|---|
| `Curiosidad` | Quieres saber algo que no sabes: la respuesta llega al final |
| `Problema` | Toca un fallo o una molestia que el espectador tiene, y la resuelve |
| `Deseo` | Enseña algo que apetece tener, comer o conseguir |
| `Identificación` | "Esto me pasa a mí": retrata algo que todos hemos vivido |
| `Sorpresa` | Pilla desprevenido: un giro que no esperabas |
| `Debate` | Invita a opinar o a llevar la contraria en comentarios |
| `Predicción` | Quieres ver cómo acaba algo que ya está en marcha |

- **`Emoción` ya no es palanca** (Gerard, 02/10/2026): todas las demás ya son emociones, así que
  no distinguía nada. Las filas que la llevaban por deducción del copy las reetiqueta Gemini
  viendo el vídeo; en las que etiquetó Gerard a mano, simplemente se quita.
- `Sorpresa` absorbe lo que antes era `Inesperado`.
- `Predicción` es querer ver cómo acaba algo que ya está en marcha (no es lo mismo que
  `Curiosidad`, que es querer saber algo que no sabes).
- **`Humor` ya no es palanca**: el humor es de qué va la pieza (`Tipo de idea = Humor`). Si
  además pilla desprevenido, la palanca es `Sorpresa`; si retrata algo que todos hemos vivido,
  `Identificación`.

## Soporte — en qué formato se publica

`Reel` (vídeo vertical corto, también el de TikTok) · `Carrusel` · `Story` · `Imagen` ·
`Vídeo largo`

No es la red: en qué red salió lo dice la columna `Redes`. Por eso `TikTok` ya no es un soporte.

## Etiquetas del cliente — ¿de qué trata en concreto?

Una columna más, **propia de cada cliente** y también con lista cerrada: es lo que distingue sus
vídeos entre sí (en Xavi, los golpes y las fases del juego: Volea, Globo, Defensa, Reto mano
izquierda…). Nunca se compara entre clientes. Vive en la base de rendimiento del cliente y sus
opciones están en `config/etiquetas.json` → `etiquetas_cliente` (no aquí, porque son de un solo
cliente).

---

## Desempates — los que fallaban

| Si dudas entre… | La regla |
|---|---|
| `Humor` (tipo) y `Humor` (palanca) | Humor solo existe como **Tipo de idea** |
| `Cliente` (tipo) y `caso-real` (plantilla) | El tipo dice *de qué va*; la plantilla, *cómo se cuenta*. Pueden ir las dos a la vez |
| `Oficio` (tipo) y `Paso a paso` / `Explicación` (formato) | El tipo es el asunto; el formato, la forma. Van juntas |
| `Comparación` (formato) y `comparativa-criterio` (plantilla) | Formato = se ven dos cosas enfrentadas. Plantilla = el guion está construido para que elijas |
| `Proceso` (formato) y `proceso-sin-voz` (plantilla) | La plantilla es la versión **sin una palabra**. Con voz explicando: formato `Proceso` + plantilla `demostracion` |
| `Día de trabajo` (tipo) y `pov-trabajador` (plantilla) | El tipo es el asunto; la plantilla es rodarlo en primera persona |
| `Trend` (formato) y una plantilla | Un trend se monta sobre un audio ajeno: formato `Trend` + plantilla `viral-original` o `replica-referencia` |
| `Interactiva` (tipo) y `Reto al espectador` (formato) | Van juntas casi siempre: una dice que pide algo, la otra qué forma tiene |

## Lo que se movió el 02/10/2026

Estas dos **eran mecánicas de guion metidas en Formato**, y ahora son plantillas con su archivo:

- `lo que se dice vs lo que se piensa` → plantilla **`dicho-vs-pensado`**
- `realidad exagerada` → plantilla **`realidad-exagerada`**

Y estas se fusionaron o se movieron de columna (lo aplicó
`infra/notion/etiquetas_sincronizar.py`, que también reescribió las filas ya etiquetadas):

| Antes | Ahora |
|---|---|
| Tipo: `Educativa`, `Receta` | Tipo `Oficio` (+ Formato `Paso a paso` si daba instrucciones) |
| Tipo: `Detrás de cámaras` | Tipo `Día de trabajo` |
| Tipo: `Caso real` | Tipo `Cliente` |
| Tipo: `Ubicacion` | Tipo `Local y zona` |
| Tipo: `Tendencia` | Formato `Trend` |
| Tipo: `Regalar producto calle` | Tipo `Producto` + Formato `A pie de calle` |
| Tipo: `Dia de trabajo` (duplicado en Formato) | solo Tipo `Día de trabajo` |
| Formato: `Ranking`, `Top 10`, `Lista` | Formato `Lista / Top` |
| Formato: `Receta` | Formato `Paso a paso` |
| Formato: `Explicacion` | Formato `Explicación` |
| Formato: `interactivo espectador` | Formato `Reto al espectador` |
| Formato: `interaccion calle` | Formato `A pie de calle` |
| Formato: `Foodporn` | Formato `Producto en primer plano` |
| Formato: `Predicción` | Palanca `Predicción` |
| Formato: `Dia de trabajo` | Tipo `Día de trabajo` |
| Palanca: `Inesperado` | Palanca `Sorpresa` |
| Palanca: `Humor` | Tipo `Humor` |
| Plantilla: `proceso-explicado` (no existía como archivo) | Plantilla `demostracion` |
| Soporte: `TikTok`, `Vídeo`, `Serie` | Soporte `Reel` · `Otro` → vacío |
