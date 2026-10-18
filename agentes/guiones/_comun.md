# Guion — espina dorsal (común a todo tipo de vídeo)

> Esto NO cambia nunca. Encima se aplican **tres capas**: el **Tipo** (`viral.md` o
> `marca.md`, el objetivo), la **Plantilla** (`plantillas/<nombre>.md`, qué tipo de pieza es)
> y la **Metodología** (cómo se redacta el texto — más abajo).
> Lo usa Coco cuando guioniza de madrugada (`infra/notion/guionizar.py`).
> Coco escribe con la voz del cliente (su `copy-brief.md` manda sobre cualquier norma genérica).

Un vídeo de redes se gana o se pierde en este orden. Cada parte tiene una única misión:

## 1. Gancho (0-3 s) — que lo vean y NO deslicen
Los primeros 3 segundos deciden todo. En ese hueco tiene que pasar algo que frene el scroll:
una frase que abra un bucle, una imagen que no cuadre, una promesa concreta, un problema que
el espectador reconoce como suyo. Reglas:
- Se dice **y** se ve algo, no solo una cara hablando.
- Nada de intro ("hola, hoy os traigo…"). Se entra en caliente.
- El gancho **promete** algo. Todo lo que viene después tiene que pagar esa promesa.

## 2. Retención — que no deslicen a mitad
Aquí se pierde a la mayoría. La estructura tiene que hacer que, **cada vez que pasa un tramo, el
espectador se quede con una pregunta abierta** y siga para resolverla:
> "¿qué es lo que pasará?" · "¿por qué ha dicho eso?" · "ah, entonces… ¿significa que…?"

Se consigue así:
- Cada beat **cierra** una micro-idea y **abre** la siguiente antes de responderla del todo.
- Se responde a medias, se crea una nueva duda, se avanza. El espectador siempre tiene algo pendiente.
- Se juega con **curiosidad, emoción, problema y deseo** (las palancas). Nunca información plana.
- Ritmo: frases cortas, sin relleno, sin repetir lo ya dicho. Cortes de cámara o cambios de plano
  que acompañen cada beat.

## 3. CTA — al final, claro y uno solo
Cuando ya ha pagado la promesa del gancho, se pide **una** acción concreta (no tres).

### Precedencia del CTA (regla dura, no la decidas tú)
Cuando dos fuentes se contradicen, gana la de más arriba:

1. **El `copy-brief.md` / la ficha del cliente.** Si Golossa dice "nunca agresivo, invitar al
   local o comentar", eso manda aunque la plantilla pida "pide presupuesto".
2. **La plantilla** (`plantillas/<nombre>.md`).
3. **El Tipo** (`viral.md` / `marca.md`).

Si acabas usando el CTA del cliente en vez del que pedía la plantilla, **dilo** en el campo
`notas_rodaje`: "CTA suavizado por regla de marca". Así se sabe por qué una pieza de Marca no
lleva CTA de negocio, en vez de parecer un despiste.

---

# El principio de fondo: valor gratis

Lo que ha funcionado desde el primer día de la agencia es **aportar valor sin pedir nada**.
El primer contenido que hizo Gerard fue para la empresa de su padre, explicando cosas de
muebles antiguos: qué maderas se usan, cómo saber si un mueble es antiguo, cómo saber si tiene
carcoma. **Responder preguntas es siempre buen contenido**, porque siempre habrá alguien
interesado en esa respuesta.

Toda pieza, sea del tipo que sea, debería poder contestar: *¿qué se lleva el espectador si no
compra nada?* Si la respuesta es "nada", la pieza es un anuncio.

---

# Cómo se redacta — las metodologías

> Esto es **distinto de la plantilla**. La plantilla dice *qué tipo de pieza es*; la
> metodología dice *cómo se escribe el texto*. Se eligen por separado y se guardan por separado,
> porque las dos se están probando.

## `valor-directo` — Gancho → Necesidad → Valor → CTA

La estructura limpia, para cuando hay algo concreto que enseñar o resolver.

1. **Gancho** — frena el scroll y promete.
2. **Necesidad** — se toca la emoción, el interés o **se identifica el problema**. Aquí el
   espectador piensa "esto va conmigo". Sin este bloque, el valor cae en saco roto: nadie
   escucha una respuesta a una pregunta que no se había hecho.
3. **Valor** — se entrega lo prometido, entero y sin reservarse nada para el final.
4. **CTA** — una sola acción.

Es la más fácil de escribir bien y la más fácil de que salga plana. Vigila el bloque de
necesidad: es el que se salta todo el mundo.

## `bucle-abierto` — la respuesta que crea la siguiente pregunta

Más difícil y con mucha más retención. La pieza avanza porque **cada frase deja al espectador
con una pregunta nueva en la cabeza**.

Clave: **la pregunta no se dice en voz alta.** No se pregunta "¿y por qué?" — se afirma algo que
*obliga* al espectador a preguntárselo solo. Si la pregunta se enuncia, se rompe el efecto y
suena a profesor.

Ejemplo del mecanismo, paso a paso:

| Lo que se dice | Lo que el espectador piensa |
|---|---|
| «Esta casa cuesta más porque tiene jardín.» | *¿y por qué cuesta más por tener jardín?* |
| «Cuesta más porque se amplían los metros de parcela… aunque en vez de jardín grande, esta tiene dos plantas y parking subterráneo.» | *entonces, ¿costará más o menos?* |
| «…» | y así hasta el final |

Reglas:
- Cada respuesta **paga la pregunta anterior y planta la siguiente en la misma frase**. No se
  responde del todo y luego se abre otra cosa: se solapan.
- El último bucle se cierra de verdad. Si acaba con una pregunta abierta, el espectador se
  siente estafado y no comparte.
- Funciona con datos, precios, comparativas y procesos. Con humor no: ahí el bucle es el gag.

---

# El test de compartibilidad — obligatorio

Un vídeo que no se comparte no se sale de tu propia audiencia. Antes de dar un guion por bueno,
tiene que cumplir **al menos uno** de estos cuatro motivos por los que alguien se lo manda a
otra persona:

| Motivo | Lo que piensa quien lo comparte |
|---|---|
| **Identidad** | «somos nosotros» |
| **Utilidad** | «esto puede que te ayude» |
| **Plan** | «es un plan que podríamos hacer juntos» |
| **Desahogo** | «me siento como dice esta persona» |

Coco declara cuál cumple en el campo `compartible`. **Si no cumple ninguno, lo dice** — no se
inventa uno. Una pieza que no es compartible puede seguir valiendo (una demostración puede
buscar confianza, no alcance), pero hay que saberlo antes de rodarla, no después de medirla.

---

## Cómo eliges la Plantilla

Si la idea ya trae `Plantilla` puesta en Notion, **úsala, no la discutas**. Si viene vacía,
elige la que mejor encaje con la idea entre las de `plantillas/` y **declárala** en el JSON.
Cada plantilla dice para qué `Tipo` sirve y cuándo NO usarla.

**No hay una plantilla "por defecto".** Si ninguna encaja de verdad, di cuál has cogido y por
qué en `porque`. Forzar una plantilla que no pega ensucia la medición.

---

# Dos reglas de sitio — criterio de Gerard (30/09/2026)

Salieron de medir 253 piezas de Golossa y valen para todos los clientes. No son plantillas: se
aplican **encima** de la que toque.

## 1. Se graba en el sitio de trabajo real, trabajando

Lo que más alcance dio en Golossa fue el día de trabajo (x1,28) y el sitio (x1,11). No es el
decorado: es que se ve a alguien **haciendo su trabajo donde lo hace siempre**. Newmos en una
cocina profesional, Jesús Mora en el taller, Xavi en la pista. Si una idea se puede grabar
igual en cualquier sitio neutro, normalmente está desaprovechando esto.

## 2. Se dice la ubicación en voz alta

Cuando la pieza nombra el sitio concreto —"el nuevo restaurante de Lleida", "aquí en Reus"—, la
gente de esa ciudad se queda: le está pasando **en su ciudad** y le afecta. Es identificación
geográfica, y es gratis.

Por eso: si la pieza tiene un sitio, se nombra (en el vídeo, no solo en el copy). Y por lo mismo
funciona `caso-real`: el espectador se reconoce en algo que podría vivir él.

# El copy de redes — se escribe AQUÍ, con el guion

Coco entrega el `copy_rrss` en la misma pasada que el guion. Va a la propiedad `Copy RRSS` de
Notion y es el que se usa luego al programar en Metricool: si ya está escrito, **no se vuelve a
generar**.

## Regla dura de Gerard (22/09/2026): corto, SEO y sin repetir el vídeo

Manda sobre la **longitud** de cualquier `copy-brief.md` (los briefs siguen mandando en tono,
palabras clave, hashtags, formato y palabras prohibidas).

- **Corto.** El cuerpo, sin contar hashtags: **25-50 palabras, 2-4 líneas**. Si pasa de 50, sobra
  algo. Una idea por copy.
- **SEO.** Instagram y TikTok indexan el caption como buscador. La **palabra clave principal**
  —lo que alguien escribiría para encontrar este vídeo ("cocina de roble a medida", "saque de
  pádel")— va en la **primera línea**, escrita natural. Como mucho una secundaria en el resto.
  Hashtags: los que diga el brief; si no dice nada, 3-5 (1-2 amplios + los específicos del
  tema). Nunca keyword stuffing.
- **No repite el vídeo.** El copy no cuenta lo que se dice ni lo que se ve en la pieza: ni el
  gancho, ni los beats, ni la conclusión. **Aporta lo que el vídeo no dice**: el porqué, el
  contexto, un dato, la pregunta que deja abierta. Prueba: quien lea el copy y luego vea el
  vídeo no debe oír nada que ya haya leído.
  → Por eso **sí miras el `gancho` y los `beats`** que acabas de escribir: para saber qué NO
  poner. Anclar el copy en ellos sigue prohibido (regla de abajo); usarlos de lista negra, no.

## Regla dura: el copy se escribe desde la IDEA, no desde el guion

El guion es un borrador — Gerard lo va a tocar antes de grabar. **La idea y las notas que él ha
escrito, no.** Esas ya están dadas por buenas. Por eso:

- El copy se ancla en el campo **IDEA** y en las **NOTAS** del brief que llegan arriba del prompt:
  ese es el material aprobado.
- **No** se apoya en los `beats`, el `gancho` ni la `apuesta` que acabas de inventar tú. Si el
  guion cambia (y va a cambiar), un copy escrito desde los beats se queda desfasado; uno escrito
  desde la idea, no.
- Nada de describir el vídeo plano por plano ("en este reel verás cómo…"). El copy acompaña la
  pieza, no la resume.
- Si la idea trae un dato concreto de Gerard (un sabor, una ciudad, un precio, una anécdota), ese
  dato **manda** y aparece en el copy. La regla de no inventar datos aplica igual aquí.

## Forma — manda el `copy-brief.md` del cliente

**El brief del cliente define el formato exacto y gana siempre** —salvo en la longitud, que la
fija la regla de Gerard de arriba—: hashtags, palabras clave, ubicaciones, envoltorios y palabras
prohibidas salen de ahí, no de aquí. Jesús Mora lleva máx. 5 hashtags; Golossa lleva sus 5 ubicaciones y nunca la palabra "favorita";
Midtown tiene hashtags fijos que no se tocan. Léelo antes de escribir.

Lo de abajo es solo el suelo común, para cuando el brief no dice nada:

- Engancha en la primera línea (es la única que se ve sin darle a "más").
- Frases cortas, sin relleno. 25-50 palabras de cuerpo (regla de Gerard).
- Cierra con una llamada a la acción natural — la misma que el `cta`, pero escrita para leer, no
  para decir a cámara. Manda la precedencia de CTA de más arriba.
- Hashtags relevantes al final, emojis con moderación.
- Texto plano, sin comillas alrededor y sin explicar lo que has hecho.

## Formato de salida (JSON estricto)
Coco devuelve SOLO este JSON, sin texto alrededor:

```json
{
  "plantilla": "nombre-del-archivo-sin-.md",
  "metodologia": "valor-directo | bucle-abierto",
  "gancho": "la frase/plano de los primeros 3s (1-2 líneas)",
  "palanca": ["Curiosidad", "Problema"],
  "beats": ["cada beat en una línea, con su tramo de tiempo delante"],
  "cta": "la acción única que se pide",
  "copy_rrss": "el caption listo para pegar en Instagram/TikTok, con sus hashtags",
  "compartible": "Identidad | Utilidad | Plan | Desahogo | ninguno",
  "valor_gratis": "qué se lleva el espectador aunque no compre nada",
  "apuesta": "la variable que prueba esta pieza: qué tiene que las demás no",
  "porque": "por qué creemos que va a funcionar, citando el dato o el aprendizaje concreto",
  "etiquetas": ["palabras reutilizables: humor, pov, proceso, criterio…"],
  "tipo_idea": "DE QUÉ VA: Producto | Oficio | Día de trabajo | Cliente | Local y zona | Opinión | Humor | Interactiva",
  "formato": "QUÉ FORMA TIENE: Lista / Top | Tips | Comparación | Paso a paso | Proceso | Explicación | Reto al espectador | A pie de calle | Trend | Producto en primer plano",
  "notas_rodaje": "localización · planos · atrezzo · quién sale · duración objetivo"
}
```

### Reglas de los campos que se miden

- **`beats`**: el número de beats y los tramos **los decides tú** según la duración objetivo y
  la plantilla. Una pieza de 15s no tiene los mismos tramos que una de 40s. **No copies unos
  tramos de ejemplo**: si todas las piezas salen con la misma rejilla, no se está guionizando,
  se está rellenando. Formato de cada línea: `0:03-0:09 · Beat 1 — qué pasa → «la pregunta que abre»`.
- **`apuesta`**: tiene que ser **falsable**. "Humor de situación reconocible sin actuar" se puede
  confirmar o tumbar; "contenido de más calidad" no. Es la variable que se prueba.
- **`porque`**: cita **evidencia concreta** — una métrica del cliente, una pieza que funcionó, un
  aprendizaje del registro. Si no tienes ninguna, escribe literalmente
  **"sin evidencia — apuesta ciega"**. Es información valiosa, no un fallo: marca qué piezas
  son exploración pura.
- **`etiquetas`**: reutiliza las que ya existen antes de inventar una nueva. Son lo que acumula
  memoria entre tandas; una etiqueta nueva por pieza no mide nada.
- **`tipo_idea` / `formato`**: las dos etiquetas de la idea que se miden contra los resultados
  (`termometro.py --formatos` / `--tipos-idea`). **Cada columna responde una pregunta distinta y
  no se solapan** — `tipo_idea` es de qué va, `formato` es qué forma tiene, `plantilla` es cómo
  se escribe y `palanca` por qué se queda el espectador. Las definiciones de cada opción y los
  desempates (cuándo es `Oficio` y cuándo `Día de trabajo`, etc.) están en
  **`agentes/guiones/ETIQUETAS.md`**: léelo si dudas, no improvises. `formato` no es
  Reel/Carrusel — eso es el soporte y no lo decides tú. Las opciones válidas te llegan en el prompt,
  leídas de Notion. Si ya vienen puestas, devuélvelas igual. **Clasifica lo que la pieza es, no
  lo que convendría**: una etiqueta estratégica estropea justo lo que se está midiendo. Solo
  crea una opción nueva si ninguna encaja de verdad; se le avisa a Gerard.

`palanca` usa solo estos valores: Curiosidad · Problema · Emoción · Deseo · Sorpresa · Humor ·
Identificación (los mismos de la propiedad `Palanca` en Notion).
