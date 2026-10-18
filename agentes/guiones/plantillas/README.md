# Plantillas de guion — el banco de mecánicas

> Creado el 13/08/2026, reestructurado el 14/08 con el criterio de Gerard: **un molde solo
> funciona si el contenido es predecible.** Antes había 2 plantillas y ninguna forma de saber
> cuál funcionaba, porque no quedaba registrado con cuál se había hecho cada pieza.

> 📌 **Qué va en cada columna** (Tipo de idea · Formato · Plantilla · Palanca), con la
> definición de cada opción y los desempates: **`agentes/guiones/ETIQUETAS.md`**. Reordenado el
> 02/10/2026; las listas son cerradas y se aplican con `infra/notion/etiquetas_sincronizar.py`.

## Las capas (no se confunden)

| Capa | Qué decide | Dónde vive | Valores |
|---|---|---|---|
| **Tipo** | El **objetivo** | Propiedad `Tipo` en Notion | Viral · Marca |
| **Plantilla** | **Qué tipo de pieza es** | Propiedad `Plantilla` | las de esta carpeta |
| **Metodología** | **Cómo se redacta el texto** | Propiedad `Metodologia` | `valor-directo` · `bucle-abierto` |
| **Tipo de idea** | **De qué va la idea** | Propiedad `Tipo de idea` | Educativa · Humor · Tendencia · Producto · … (abierto) |
| **Formato** | **La forma del contenido** | Propiedad `Formato` | Tips · Top 10 · Ranking · Lista · Comparación · … (abierto) |
| **Autor** | **Quién propuso la idea** | Propiedad `Autor` | Gerard · Oli · Andrea · Cliente |

> ⚠️ 22/09/2026: `Formato` es el del **contenido**. Reel/Carrusel/Story es `Soporte`.

> Tipo de idea, Formato y Autor (22/09/2026) están en la Bandeja y en todas las bases de cliente. Son
> **abiertas**: las opciones viven en Notion y se añaden allí a mano; Coco las lee en vivo.
> Detalle y migración en `infra/notion/etiquetas_idea.py`. Se miden con
> `termometro.py [<cliente>] --ideas`. Un Formato no es una Plantilla: un "Top 5" se puede
> escribir como `error-mito` o como `criterio-detalle`.

Las tres se guardan por pieza porque **las tres se están probando**. La metodología está
explicada en `../_comun.md`, no aquí: aplica a todo, no a una plantilla concreta.

## Moldes de MARCA — 11

Describen una forma repetible: cambias el tema y siguen funcionando. Un vídeo de marca es
predecible, y por eso un molde lo escribe bien.

| Plantilla | Qué es | Evidencia |
|---|---|---|
| `demostracion` | Algo funcionando delante de la cámara | 🟢 Newmos: su mejor formato medido |
| `criterio-detalle` | Lo que no se ve de algo bien hecho | 🟡 Jesús Mora, herrajes: x1,6 |
| `pregunta-real` | Responder lo que la gente se pregunta del oficio | 🟢 el formato con el que arrancó la agencia |
| `comparativa-criterio` | Varios que parecen el mismo: cuál falla | 🟡 hipótesis jm-09-4 |
| `error-mito` | Te han contado esto mal | 🟡 ya usado sin nombre (Xavi, Golossa) |
| `antes-despues` | La transformación | 🟡 el vídeo más visto de Jesús Mora, sin repetir |
| `caso-real` | Un encargo, de principio a fin | 🔴 la pieza del set de Golossa que factura directo |
| `proceso-sin-voz` | De materia prima a producto, sin una palabra | 🔴 sin probar |
| `historia-a-camara` | El cliente cuenta, no explica | 🔴 **control** |
| `pov-trabajador` | El día desde dentro | 🟢 Midtown: los POV rinden, los sketches no |
| `objecion` | La razón por la que no te compran | 🔴 **sin ninguna evidencia**, hueco de conversión |
| `secreto-del-oficio` | Lo que en el sector no se cuenta (material, medidas, receta, equipo) | 🟢 Golossa: las 3 piezas con MÁS interacción de la cuenta (9,1-9,2%, x3,3) |
| `opinion-marcada` | La opinión profesional que pincha y hace comentar | 🟡 Golossa: `Opinión` es la etiqueta con más interacción (x1,21); poco alcance por sí sola |

## Procesos de VIRAL — 2

**No son moldes y no lo van a ser.** Lo que hace funcionar un viral es exactamente lo que tenía
*ese* vídeo concreto; un molde genérico describe una categoría, no una mecánica.

| Proceso | Cuándo | Input |
|---|---|---|
| `replica-referencia` | Hay un vídeo guardado que funcionó | **El desglose de Gerard**, no el enlace |
| `viral-original` | No hay referencia: la idea se inventa | Restricciones + criterios de descarte |

> ⚠️ **Coco no puede abrir un enlace de Instagram** (comprobado 14/08: devuelve vacío siempre;
> TikTok sí funciona). Y aunque pudiera, no puede *ver* el vídeo. Por eso `replica-referencia`
> exige 2-3 líneas de desglose humano, y sin ellas la idea no se guioniza.

## Qué pasó con `humor-situacion` y `comparativa-duelo`

Borradas el 14/08. Estaban escritas como moldes de escritura cuando son mecánicas virales:
describían una categoría ("haz algo reconocible") con la que no se puede escribir nada.

Lo que valía de ellas —**el dato de que el humor reconocible y el duelo funcionan**— se
conserva en dos sitios: como **patrones medidos** dentro de `viral-original.md`, y como
**etiquetas** (`humor`, `situacion-reconocible`, `comparativa`, `interaccion`), que es donde el
termómetro ya lo agregaba.

## Los dos ejes: para qué sirve cada mecánica (29-30/09/2026)

Desde Golossa se mide en **alcance** e **interacción**, y no siempre van juntos. Elegir plantilla
es elegir qué se busca:

| Si buscas… | Tira de | Evidencia (Golossa) |
|---|---|---|
| **Comunidad, guardados, comentarios** | `secreto-del-oficio`, `opinion-marcada`, explicación | interacción x1,08-x3,3 |
| **Alcance** | `pov-trabajador` / día de trabajo, ubicación reconocible, `caso-real` | vistas x1,1-x1,28 |

Un viral sin interacción no construye nada: *"Aquí siempre pilla el mismo"* hizo **x72 en vistas
con un 0,8 % de interacción**. Sirve de recordatorio, no de objetivo.

## Cómo se testea

1. En una tanda, **no repitas la misma plantilla en todas las piezas**. El modelo es la tanda
   de Jesús Mora de septiembre: 8 piezas deliberadamente distintas. No se busca que funcionen
   las 8, se busca saber cuál funciona.
2. **Una plantilla no concluye con una pieza.** Por eso se reutilizan entre tandas y clientes.
3. **Mete siempre una pieza de control**: una que creas que va a fallar, para cerrar una
   discusión con un dato en vez de con una opinión.
4. Para leer los resultados:
   ```bash
   python3 "infra/estado/termometro.py" <cliente> --plantillas
   python3 "infra/estado/termometro.py" --plantillas
   ```

⚠️ La columna de evidencia hay que actualizarla al cerrar cada tanda. Si se queda vieja, vuelve
a ser opinión disfrazada de dato.
