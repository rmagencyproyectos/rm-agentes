# Carruseles IA Golossa — idea -> prompts -> diseño por capas

Flujo para crear carruseles de Golossa con imagen generada por IA y texto editable por capas en
Cloud Design. La imagen generada es la base visual; los textos, logos, sellos y ajustes finales
se montan encima como elementos editables, no como JPG cerrado.

## Principio

Golossa no debe parecer una pastelería corporativa. Es una marca de entretenimiento que vende
cheesecakes, cookies y antojo. Cada carrusel tiene que competir en el feed con humor, exageración,
textura apetecible y una idea fácil de entender en el primer vistazo.

Hay dos líneas creativas:

- **Realista**: foto hiperrealista, producto muy apetecible, iluminación cálida, textura creíble,
  nada que huela a IA. Puede parecer editorial, macro food, laboratorio, backstage o making-of.
- **Exagerada IA**: situación imposible, absurda o espectacular. Debe notarse que la premisa es
  generada con IA, pero seguir viéndose premium, limpia y golosa.

## Kit Visual

Kit de marca local:

`/Volumes/DD 2 TB WORK/Golossa/Kit de Marca`

Elementos detectados:

- Logo: `Kit/Logo Golossa.png`
- Mascota: `Golossin.png`, `Golossin action.png`
- Tipografías: `Montra-FreePersonalUse.otf`, familia `Montserrat`
- Colores base del kit:
  - Crema: `#f9dfb9`
  - Marrón chocolate: `#3f3023`

Uso recomendado:

- Fondo cálido/crema o escena con dominante cálida.
- Marrón chocolate para textos y marca.
- Montserrat para textos legibles, CTAs, subtítulos y etiquetas.
- Montra para títulos expresivos o una palabra protagonista.
- Golosín aparece en la mayoría de carruseles como actor, guía, reacción o sello de marca.

## Producto Real - Cookie Red Velvet

Esta regla manda sobre cualquier prompt genérico de "food photography". Las cookies de Golossa no
son galletas planas ni perfectas: son piezas gruesas, abombadas y artesanales.

### Forma

- Cookie alta, abombada, tipo montículo de masa horneada.
- No plana, no circular perfecta, no simétrica.
- Hecha con las manos: laterales irregulares, zonas comprimidas, pliegues y grietas naturales.
- Si aparece partida, debe verse rota de forma imperfecta, sin aplastar la cookie.
- La pieza debe mantener volumen incluso cuando se abre o se muerde.

### Textura Exterior

La textura real no es "smooth" en sentido pulido. Es masa densa y horneada.

- Superficie mate, nunca brillante/plástica.
- Masa compacta de Red Velvet, no bizcocho, no crumble seco.
- Menos hoyitos pequeños; evitar poros uniformes de esponja.
- Grietas grandes, pliegues irregulares y roturas naturales.
- Zonas algo lisas por presión de la masa, pero con imperfecciones reales.
- Color rojo profundo/burdeos, con variación natural; nunca rojo neón ni sobresaturado.
- Luz de estudio natural y controlada, no highlights exagerados ni acabado de render.

### Relleno

- Interior más apetecible que la foto real, pero sin pasarse.
- Capa de crema visible, cremosa y blanca, integrada dentro de la masa.
- No debe parecer lava, queso fundido, salsa desbordada ni relleno imposible.
- Al partirla: borde irregular, migas reales, crema contenida.

### Toppings

- Todos los toppings van arriba.
- El chocolate blanco va encima de la cookie, normalmente sobre la parte alta o lomo superior.
- Nunca poner el chocolate blanco en el lateral como si estuviera pegado fuera.
- El drizzle blanco va encima, con líneas imperfectas y algún goteo natural.
- Evitar líneas demasiado perfectas, brillo plástico o exceso de glaseado.

### Palabras Peligrosas

Evitar o matizar estas palabras porque tienden a producir resultados falsos:

- "smooth" sin explicar que es masa mate y artesanal.
- "glossy", "shiny", "perfect", "ultra polished".
- "hyperrealistic food ad" si empuja demasiado brillo.
- "crumbly" si lo convierte en bizcocho seco o superficie porosa.

Usar en su lugar:

- "dense baked red velvet cookie dough"
- "matte handmade surface"
- "large natural cracks and folds"
- "compressed dough areas"
- "muted deep red/burgundy"
- "soft diffused studio light"
- "real product photography, not render"

### Protocolo De Iteración

Cuando haya una referencia real de producto:

1. Primero se valida **solo la textura y forma** con una slide/patrón.
2. No se generan las 5 slides hasta que Gerard apruebe esa textura.
3. Una vez aprobada, esa pauta se copia a todos los prompts del carrusel.
4. No subir a Drive ni cerrar Notion hasta tener OK del set final.

### Acabado Aprobado - Cookie Red Velvet

Pauta extraída de las pruebas aceptadas del carrusel "Partes de una cookie":

- Base visual: foto de estudio realista, no render, no anuncio hiperbrillante.
- Composición: cookie en pedestal redondo de madera clara, fondo marrón cálido, mucho espacio
  limpio arriba para texto por capas.
- Luz: cálida y suave, de estudio, con sombras controladas. Debe apetecer, pero sin brillos
  agresivos ni reflejos artificiales.
- Color: Red Velvet rojo vivo pero natural. Más rojo que burdeos apagado, pero nunca neón.
- Masa: densa, compacta y horneada. La textura tiene volumen y grietas, pero no debe parecer
  bizcocho, espuma, plástico ni superficie mojada.
- Forma: muy abombada, gruesa, artesanal, como un montículo hecho con las manos.
- Toppings: siempre arriba. Chocolate blanco sobre el lomo superior; drizzle blanco imperfecto,
  con caídas naturales frontales.
- Relleno/interior: apetecible y cremoso, pero contenido; nada de lava ni exceso imposible.

Prompt base recomendado para futuras cookies:

```text
Create a vertical 4:5 Instagram carousel background for Golossa Cakery, realistic studio food
photography, no text. Use the real reference cookie as strict product guide.

One thick domed handmade Red Velvet cookie on a light round wooden pedestal, warm chocolate-brown
studio background, clean negative space in the upper half for editable Cloud Design text.

The cookie must look like a real Golossa cookie: high mound shape, dense baked dough, handmade
irregular folds, compressed areas, natural cracks, compact texture, not flat and not symmetrical.
Red Velvet color: vivid natural red, appetizing, with subtle darker baked areas; not neon, not dull
brown.

All toppings are on top: a pale white chocolate half-disk on the upper ridge, and imperfect white
cream-cheese drizzle lines with a few natural front drips. Keep the drizzle creamy but not plastic.

Lighting: warm soft diffused studio light, controlled natural shadows, appetizing but realistic.
Avoid glossy ad highlights, wet-looking dough, plastic shine, sponge pores, fake pebble texture,
perfect symmetry, side-mounted chocolate, extra toppings, text, logos, watermark, hands, packaging.
```

Postproducción segura:

- Si una imagen gusta pero tiene demasiado brillo, NO regenerarla con IA.
- Hacer ajuste fotográfico local: bajar highlights, reducir brillo especular en rojos, subir o
  equilibrar el rojo si hace falta.
- No redibujar la cookie para corregir brillo, porque el modelo tiende a plastificar y ordenar la
  textura.

## Gates

No saltarse el orden:

1. **Idea principal**: concepto, objetivo, tono, número de slides y por qué puede funcionar.
2. **Aprobación de Gerard**: sin OK no se escriben prompts completos.
3. **Prompt base del carrusel**: dirección visual común y resumen de las slides.
4. **Aprobación de Gerard**: sin OK no se generan prompts avanzados.
5. **Prompt avanzado por slide**: un prompt independiente por imagen.
6. **Generación de imágenes** en ChatGPT Imagen.
7. **Montaje en Cloud Design**: JPG como fondo + textos/logos/capas editables.
8. **OK final de Gerard** antes de publicar o programar.

Como en el resto del sistema: nada se envía al cliente ni se programa en Metricool sin OK explícito.

## Estructura de una idea

```yaml
cliente: golossa
formato: carrusel_ia
linea: realista | exagerada_ia
serie_recurrente: true | false
titulo: ""
promesa: ""
producto: cheesecake | cookie | cheeseshake | mix
objetivo: alcance | guardados | comentarios | visitas_tienda
slides: 5
golosin: protagonista | guia | cameo | sello_final | no
estado: idea | idea_aprobada | prompt_base | prompt_base_aprobado | prompts_slide | imagenes | cloud_design | listo_revision
notas: ""
```

## Prompt Base

El prompt base no genera todavía todas las imágenes definitivas. Sirve para aprobar dirección.

Debe incluir:

- Línea: realista o exagerada IA.
- Producto protagonista.
- Estética Golossa: cálida, joven, divertida, crema/marrón, antojo, nada corporativo.
- Papel de Golosín.
- Número de slides.
- Qué cuenta cada slide en una frase.
- Qué textos irán por capas en Cloud Design.

Plantilla:

```text
Carrusel IA para Golossa Cakery.

Linea visual: [realista / exagerada IA].
Producto protagonista: [cookie / cheesecake / cheeseshake].
Objetivo: [comentarios / guardados / visitas / alcance].
Tono: joven, divertido, apetecible, TikTok, cero corporativo.
Marca: usar paleta Golossa crema #f9dfb9 y marron chocolate #3f3023. Textos posteriores en
Montserrat/Montra desde Cloud Design, no integrados en la imagen.
Mascota: Golosin [protagonista / guia / cameo / sello].

Idea: [concepto principal].
Estructura de 5 slides:
1. [slide 1]
2. [slide 2]
3. [slide 3]
4. [slide 4]
5. [slide 5]

Restricciones:
- No incluir texto legible dentro de la imagen generada salvo rotulos ambientales inevitables.
- Dejar zonas limpias para titulares editables.
- Producto muy apetecible: textura, brillo, cremosidad, miga, relleno o topping.
- Imagen vertical 4:5 para carrusel Instagram.
```

## Prompt Avanzado Por Slide

Cada slide se genera como imagen independiente. El texto definitivo va fuera, por capas.

Plantilla:

```text
Create a vertical 4:5 image for an Instagram carousel background for Golossa Cakery.

Visual line: [hyper-realistic premium food photography / obviously AI surreal exaggerated scene].
Slide [N] of 5.
Scene: [descripcion precisa].
Main subject: [producto].
Golosin: [pose/papel de la mascota, si aparece].
Composition: [primer plano / plano cenital / vitrina / museo / laboratorio / etc.].
Lighting: warm, appetizing, high contrast, creamy highlights, rich chocolate-brown shadows.
Brand feeling: young, playful, delicious, not corporate, TikTok-native.
Color palette: warm cream #f9dfb9, chocolate brown #3f3023, baked golden tones.
Leave clean negative space for editable text overlays in Cloud Design: [zona].

Important:
- No readable text, no random letters, no watermark, no logos generated by AI.
- Make the food look extremely appetizing.
- Avoid plastic-looking textures, distorted hands, fake typography, uncanny faces.
- If Golosin appears, keep him as a cheerful cheesecake-slice mascot with white gloves,
  black limbs, brown sneakers and expressive cartoon face.
```

## Series Recurrentes

### Realistas

1. **Anatomia de una cookie**
   - Promesa: "Por que esta cookie engancha tanto".
   - Slides: masa, relleno, topping, horneado, mordisco final.
   - Golosín: guía/cameo señalando partes.
   - Útil para: guardados y producto.

2. **Radiografia de una cheesecake**
   - Promesa: "Lo que no ves cuando la cortamos".
   - Slides: base, crema, topping, corte perfecto, cucharada.
   - Golosín: científico/inspector.
   - Útil para: antojo y comentarios.

3. **Manual de emergencia para antojos**
   - Promesa: "Síntomas de que necesitas Golossa".
   - Slides: antojo, indecisión, vitrina, elección, solución.
   - Golosín: doctor del antojo.
   - Útil para: humor suave y visitas.

### Exageradas IA

1. **La cookie en el museo**
   - Promesa: "Cuando una cookie merece vitrina".
   - Slides: vitrina, cola de gente, flashes, seguridad, Golosín presentando la obra.
   - Golosín: guía de museo o guardia.
   - Útil para: alcance y compartidos.

2. **Juicio por comerse la ultima cheesecake**
   - Promesa: "Declarado culpable de no compartir".
   - Slides: tribunal, prueba del mordisco, testigos, veredicto, condena dulce.
   - Golosín: juez/fiscal.
   - Útil para: comentarios.

3. **NASA detecta una cookie**
   - Promesa: "Objeto no identificado: demasiado bueno".
   - Slides: radar, sala de control, cookie flotando, alarma, aterrizaje en Golossa.
   - Golosín: astronauta.
   - Útil para: viralidad absurda.

## Textos Por Capas

Regla: la IA genera imagen sin texto. Cloud Design añade:

- Título grande, pocas palabras.
- Etiquetas cortas por slide.
- Flechas, círculos, sellos, subrayados o stickers.
- Logo Golossa pequeño donde toque.
- Golosín recortado si conviene reforzar marca.

Ejemplo para "Anatomia de una cookie":

1. "ANATOMIA DE UNA COOKIE"
2. "LA MASA"
3. "EL RELLENO"
4. "EL TOPPING"
5. "EL MORDISCO FINAL"

CTA final Golossa:

- "¿Que parte eliges tu?"
- "Etiqueta a quien no compartiria."
- "Confiesa: ¿cookie o cheesecake?"

## Criterios De Calidad

Antes de aprobar una imagen:

- ¿Da hambre en menos de un segundo?
- ¿Parece Golossa aunque tapes el logo?
- ¿Hay espacio limpio para texto?
- ¿Golosín aparece con sentido y no como adorno aleatorio?
- ¿La linea visual está clara: realista creíble o IA exagerada?
- ¿Evita textos raros, manos deformes, logos falsos y productos plastificados?
- ¿La slide funciona sola y también como parte de la secuencia?
