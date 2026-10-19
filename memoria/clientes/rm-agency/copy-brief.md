# Brief de copy — RM Agency (cuenta propia)

> 🟡 **PENDIENTE DE VALIDAR POR GERARD.** Creado el 26/08/2026 al enchufar RM a la fábrica.
> No es un brief verbatim como el de Golossa o Jesús Mora: aquí no hay instrucciones suyas
> todavía, solo el mínimo estructural para que Coco no escriba a ciegas. En cuanto Gerard diga
> cómo quiere que suene la cuenta de la agencia, esto se reescribe entero.

## Lo único que es regla dura hoy

- **No inventar datos.** Nombres de clientes, cifras de resultados, precios de servicios,
  casos de éxito: o salen de la Idea/Notas que ha escrito Gerard, o **no se escriben**. Es la
  cuenta de la propia agencia: un dato inflado aquí es una promesa comercial falsa.
- **Ningún cliente aparece por su nombre** sin que Gerard lo haya puesto explícitamente en la
  idea. Enseñar trabajo de un cliente en la cuenta de la agencia es una decisión suya, no de Coco.
- **El copy se escribe desde la IDEA y las NOTAS**, no desde los beats del guion
  (regla general, ver `agentes/guiones/_comun.md`).

## Que no huela a venta (Gerard, 14/10/2026)

- La pieza **cuenta una historia** (o juega con el espectador) y la venta aparece **solo al
  final**, en una línea de CTA. En ningún momento antes tiene que parecer que se vende algo.
- Fuera: precios y «vale X €», medidores de «compatibilidad con RM», catálogos de servicios
  con contador, maquetas de comentario con el precio tachado.
- CTA vigente: «Escribe ESTRATEGIA» → estrategia gratis, dicho en tono de favor, no de oferta.

## Carruseles de RM (Gerard, 14/10/2026)

- Máximo **10 diapositivas**. **Sin logo ni contador** («1/10») arriba.
- Cada diapositiva guía la vista: rótulo pequeño → titular corto con **la palabra clave marcada**
  → una línea de apoyo → **un dibujo/maqueta que ilustra esa frase** → «desliza →».
  Referencia que pasó Gerard: https://www.instagram.com/p/DeKy3GtF6oT/
- **Portada** (Gerard, 14/10/2026): **habla del que lee, no de nosotros**. O se reconoce
  («¿Tienes un negocio en Lleida…?») o reconoce un problema que tiene («¿No sabes qué publicar
  cada semana?»). Que un cliente nuestro creciera le da igual si no se ve reflejado.
  Limpia: una sola idea en grande, abajo solo la pregunta o «desliza»; la «tralla» empieza en la 2.
- **Color**: fondo **siempre gris** (también la portada); el rojo solo para el texto importante.
  El rojo de fondo es demasiado agresivo.
  **Excepción: la última diapositiva va al revés** (fondo #ff2041, letras en gris y en oscuro).
  Los textos secundarios, en el oscuro (#15121a), no en gris claro (revisión del 14/10/2026).
- **Hilo de preguntas** en los carruseles de historia: cada diapositiva deja abajo una pregunta
  («¿Y cómo la hicimos crecer? →»), la siguiente la repite arriba y la responde. Así hay
  continuidad y siempre un motivo para deslizar.
- Plantilla: desde el 19/10/2026 los carruseles nuevos se hacen **como datos** (pieza JSON) con
  `infra/carruseles/carrusel.py` (PNG + PDF para LinkedIn; esquema en `infra/carruseles/README.md`).
  `carruseles/_fuente/carruseles.html` (render con `slides.js`) queda como histórico de los 7 primeros.

## Forma (provisional, hasta que Gerard la fije)

- Primera línea que enganche; frases cortas; nada de jerga de agencia ("sinergias",
  "storytelling 360", "engagement orgánico").
- 3-5 hashtags al final. **TBD**: ¿hashtags fijos de marca? ¿ubicación fija?
- Emojis con moderación.

## TBD — lo que hace falta preguntarle a Gerard

1. **Objetivo de la cuenta**: ¿capta clientes o construye marca? De ahí sale el CTA.
2. **Tono**: ¿el mismo gamberro que usa en Golossa, o más sobrio por ser B2B?
3. **CTA por defecto**: ¿DM, enlace en bio, formulario, o ninguno (valor gratis puro)?
4. **Hashtags fijos y ubicación**, si los hay.
5. **¿Se pueden nombrar clientes del roster?** Y si sí, ¿cuáles.
