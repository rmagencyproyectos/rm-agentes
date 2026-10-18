# Registro de aprendizajes / correcciones (Capa 2 de memoria)

> Log **append-only**. Cada entrada = una lección aplicable. Lo escriben QA, Gerard y el
> análisis de cierre; lo leen el Estratega y el Editor antes de producir. El dato
> estructurado equivalente está en `registro.json`.
>
> Formato de entrada:
> ### [fecha] · [cliente] · [agente] · [tipo: correccion|aprendizaje|regla]
> **Qué:** … **Por qué:** … **Cómo aplicarlo:** …

---

### 2026-07-25 · todos · estratega · aprendizaje
**Qué:** el **vídeo vertical (Reels de Instagram + TikTok) manda en todos los clientes**; el
feed (imágenes/carruseles) rinde mucho menos en vistas y alcance. La red que más pega varía:
Golossa→TikTok, Midtown y MSM→Reels de Instagram, Newmos→ambas. El contenido está **duplicado**
TikTok↔Reels (mismo vídeo en las dos redes). **Por qué:** confirmado con datos de Metricool
(180 días, `memoria/metricas/<cliente>.md`). **Cómo aplicarlo:** Sun prioriza ideas de vídeo
vertical; al analizar rendimiento, mira Reels+TikTok, no el feed. Pendiente: **Xavi Colomina
no tiene cuentas conectadas en Metricool** (0 datos) — resolver para poder medirlo.

### 2026-07-24 · golossa · analisis · aprendizaje
**Qué:** un reel viral ("Es normal la indecisión") concentró ~90% del engagement del mes.
**Por qué:** el humor/relato identificable dispara el alcance mucho más que el producto solo.
**Cómo aplicarlo:** doblar la apuesta por formatos de humor/situación reconocible, no solo
cortes de producto.

### 2026-07-24 · midtown · analisis · aprendizaje
**Qué:** los vídeos de la Pantera (sobre todo sketches) son de los que peor funcionan pese
a generar confianza interna; los POV con camarero (Carles, cámara al pecho) rinden y dan
muchas piezas.
**Por qué:** lo natural/improvisado conecta más que el personaje forzado.
**Cómo aplicarlo:** priorizar POV de camarero; usar la Pantera como gancho puntual, no como
formato principal.

### 2026-07-24 · newmos · aprendizaje
**Qué:** el mejor formato es grabar en obrador industrial explicando una máquina; "educar a
cámara" sobre cosas de restaurantes no funciona.
**Por qué:** la demostración real genera más confianza que la charla.
**Cómo aplicarlo:** crear formatos repetibles de demostración; evitar talking-head educativo.

### 2026-07-25 · xavi-colomina · editor · regla
**Qué:** en el entreno Pablo/Phineas, POV/ = cámara PRINCIPAL (sigue a Xavi, protagonista)
e IMG_249X = cámara de insertos + audio de solapa. El `momentos_clave.md` etiqueta IMG como
"la cámara que sigue a Xavi", pero se refiere a que IMG tiene la VOZ (micro), no el vídeo.
**Por qué:** los planes reales de C1–C5 (`scripts/multicam/ejemplos/c*plan.json`) usan pov=POV,
fix=IMG; y el `transcripciones/sync-map.md` es la fuente de verdad de los deltas de sincronía.
**Cómo aplicarlo:** roles = los de la skill `edicion-multicam` (POV principal, IMG insertos+audio).
Antes de cortar un clip nuevo, mirar `sync-map.md`: si el segmento POV tiene delta "medido"
(snr), es fiable; si es "reloj" (±1s), refinar el delta por audio antes de renderizar.

### 2026-08-11 · jesus-mora · analisis · aprendizaje
**Qué:** lo de "a Jesús Mora no le funciona nada" es, sobre todo, **una caída de TikTok, no
un problema del contenido**. Mediana de vistas por mes: TikTok 4.133 (jun) → 2.159 (jul) →
978 (ago); Instagram 1.186 → 1.260 → 1.527, o sea **plano o subiendo**. El mismo vídeo puede
salir x1.6 en Reels y x0.2 en TikTok el mismo día (26/07 y 09/08), así que juzgar una pieza
por una sola red es ruido. **Por qué:** medido con `infra/estado/termometro.py` sobre las 40
publicaciones de 180 días (`memoria/metricas/_posts/jesus-mora.json`); agosto son solo 2
piezas, así que la última bajada aún es débil. **Cómo aplicarlo:** valorar cada pieza por la
**suma Instagram+TikTok** contra la mediana del cliente, nunca por una red suelta. Y no
rediseñar el contenido de Instagram como si estuviera fallando: no lo está.

### 2026-08-11 · todos · sistema · regla
**Qué:** ninguna pieza se produce sin **hipótesis escrita** (`apuesta` + `porque`) en
`ciclos/YYYY-MM/<cliente>/hipotesis.json`. **Por qué:** durante meses se opinó sobre qué
funcionaba sin haber apuntado nunca qué se esperaba, así que ningún resultado enseñaba nada.
**Cómo aplicarlo:** al guionizar (fase ✍️ del reloj) se rellena la hipótesis; al publicar se
pone la fecha; en la fase 📊 se cierra la tanda con `termometro.py <cliente> --cerrar` y el
aprendizaje que salga es **el input de las ideas del mes siguiente**. Detalle en
`ciclos/HIPOTESIS.md`.

### 2026-08-11 · jesus-mora · gerard · regla
**Qué:** con Jesús Mora se graba **un solo día, en el taller**. No se puede plantear nada que
exija seguir una obra o una instalación real (no va a montar una cocina para la cámara), ni
nada que exija **actuar** (no es actor: reaccionar y contar, sí). Además: **sin precios en
pantalla** por ahora, y **no se enseña trabajo mal hecho** porque no lo hay — el criterio se
transmite enseñando lo bueno de cerca. **Por qué:** Gerard lo corrigió al revisar la primera
tanda de hipótesis de septiembre; tres de las ocho eran imposibles de grabar. **Cómo
aplicarlo:** toda idea para este cliente se valida antes contra "¿sale del taller en un día?".
Está escrito en el campo `restricciones` de `ciclos/2026-09/jesus-mora/hipotesis.json`, que
se copia a las tandas siguientes.

### 2026-09-29 · todos · gerard · regla
**Qué:** una pieza se juzga por **dos ejes**, nunca solo por vistas: alcance (vistas / mediana
de su red) e **interacción** (% interacción / mediana de su red). La `Nota` es la media
geométrica de los dos. **Por qué:** regla de Gerard — 100k vistas al 1% valen menos que 50k al
10%. Con los datos de Golossa se ve literal: *"Aquí siempre pilla el mismo"* hizo **x72 en
vistas y x0,25 en interacción** (0,8%), mientras *"Hoy os enseñamos uno de nuestros secretos"*
hizo x10 en vistas pero **x3,3 en interacción** (9,2%). La primera la empujó el algoritmo; la
segunda conectó. **Cómo aplicarlo:** `infra/notion/rendimiento.py` calcula la Nota y de ella
sale el veredicto. Al cerrar tandas, mirar los dos ejes por separado antes de concluir.

### 2026-09-29 · golossa · analisis · aprendizaje
**Qué:** sobre 253 piezas (ago-2025 → sep-2026), lo que separa de verdad en la Nota **no son
las etiquetas de contenido, son cosas objetivas**: 8+ hashtags 1,35 vs 0-3 hashtags 0,81 ·
copy de más de 600 caracteres 1,35 vs 0,89 los de menos de 200 · miércoles 1,18 (el mejor día)
· vídeo (Reel 0,95 / TikTok 0,94) muy por encima de **carrusel 0,70 e imagen 0,51** · publicar
en las dos redes 0,97 vs 0,85 solo Instagram. **Por qué importa el matiz del carrusel:** por
vistas solas el carrusel parecía el mejor formato (x1,43); al meter la interacción se cae. Es
el ejemplo de por qué se miden dos ejes. **Cómo aplicarlo:** en cualquier cliente, copy
trabajado y largo + 8-10 hashtags + vídeo, y reservar el carrusel para lo que de verdad lo pida.

### 2026-09-29 · golossa · analisis · método
**Qué:** etiquetar SOLO a los ganadores no permite concluir nada. Gerard etiquetó a mano las 34
mejores piezas; al cruzarlas, toda etiqueta parecía ganadora (caso-real 3,98, demostracion
4,82…) simplemente porque las 219 restantes no tenían etiqueta. Al etiquetar el resto desde el
copy (`infra/notion/etiquetar_desde_copy.py`, marcado `Etiquetado por = Deducido del copy`) y
comparar **solo dentro de ese grupo**, ninguna etiqueta separa: todo cae entre 0,79 y 1,21.
**Por qué:** hace falta grupo de comparación, y el etiquetado desde el copy es un proxy débil
(no ve el vídeo, así que diluye diferencias reales). **Cómo aplicarlo:** cuando se quiera medir
una etiqueta, etiquetar ganadoras Y perdedoras con el mismo criterio y la misma persona. Hasta
entonces, las diferencias por etiqueta son hipótesis, no datos.

### 2026-09-29 · golossa · analisis · aprendizaje
**Qué:** separando los dos ejes en el grupo comparable, hay una tendencia suave pero coherente:
lo que **interactúa** es opinión (x1,21), educativo (x1,09) y explicación (x1,08); lo que trae
**vistas** es día de trabajo (x1,28 en formato), ubicación (x1,11) y caso real (x1,13). Las tres
piezas con más interacción de toda la cuenta son **enseñar la receta/el secreto (9,1-9,2%)** y
**un reto al espectador (9,1%)**. **Cómo aplicarlo:** si el objetivo es alcance, día de trabajo
y sitio; si el objetivo es comunidad y guardados, enseñar cómo se hace algo y pedir que elijan.

### 2026-09-30 · todos · gerard · regla
**Qué:** cuatro mecánicas sacadas de los datos de Golossa, con el porqué que les puso Gerard —
que es lo que permite trasladarlas a cualquier cliente:

1. **Enseñar un secreto del sector o de la empresa** trae visitas *y* interacción. En Golossa
   fue la receta de las cheesecakes y las cookies; en Jesús Mora puede ser el material secreto,
   las medidas secretas o el mobiliario que él no compraría; en Newmos, el equipo con el que se
   hace de verdad tal plato en los restaurantes. Plantilla nueva: `secreto-del-oficio`.
2. **La opinión genera comentarios**: hay que mojarse con una opinión marcada y profesional, y
   **pinchar un poco al público**. Plantilla nueva: `opinion-marcada`.
3. **El día de trabajo trae alcance**: grabar simulando (o haciendo) el trabajo en el sitio
   habitual — Newmos en una cocina profesional, Jesús Mora en el taller. Va con `pov-trabajador`.
4. **Decir la ubicación** retiene: si el vídeo nombra "el nuevo restaurante de Lleida", la gente
   de Lleida se queda porque está pasando en su ciudad y le influye. Y `caso-real` funciona por
   lo mismo: **identificación** — es algo que podrían vivir ellos.

**Por qué:** el análisis de las 253 piezas de Golossa (29/09) daba los números; esto les pone el
mecanismo. Sin el mecanismo, los números no se pueden trasladar a un cliente de otro sector.
**Cómo aplicarlo:** las dos plantillas nuevas están en el catálogo (Coco las ve solo); las dos
reglas de sitio, en `agentes/guiones/_comun.md`; la traducción por cliente, en la sección
"Qué funciona — ángulos a explotar" de cada `memoria/clientes/<slug>/ficha.md`, que es lo que
lee Oli al montar la tanda.
**Estado de la evidencia:** `secreto-del-oficio` 🟢 (las 3 piezas de más interacción de la
cuenta); el resto 🟡, medido en un solo cliente y de un sector distinto. Se confirma o se cae
con las tandas de octubre.
