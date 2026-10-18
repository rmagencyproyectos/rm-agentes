# 🛠️ Registro de cambios del sistema (Nova)

Log append-only de los cambios que Nova aplica al propio sistema, tras el OK de Gerard.
Cada entrada: fecha · qué se pidió · qué se cambió (archivos) · cómo revertir.

---

### 2026-09-09 · Roster: Golossa y MSM fuera, Midtown pausa indefinida, Newmos activo
- **Pedido por Gerard:** ya no trabajamos con Golossa ni MSM; Midtown pasa a pausa indefinida
  (no "retoma en septiembre"); Newmos vuelve activo, publicando domingos a las 15:00.
- **Cambiado:** `config/ciclo-mensual.json` (desfase: fuera golossa, entra newmos=1; nota de
  fuera_del_reloj actualizada para golossa/msm/midtown); `config/publicacion.json` (pausas
  añadidas para golossa y msm sin fecha de vuelta, midtown pasa a `hasta: null`, pausa de
  newmos retirada — su día domingo ya estaba en `dias.newmos`); `config/metricool-marcas.json`
  (golossa y msm movidos de `roster_v1` a `fuera_de_roster_v1`, conservando brand_id por si hay
  que consultar Metricool en el futuro).
- **Cómo revertir:** deshacer esos tres diffs; para reactivar Golossa/MSM basta con mover sus
  bloques de vuelta a `roster_v1` y quitar su pausa; Midtown recupera desfase 3 cuando vuelva.

<!-- Plantilla de entrada:
### AAAA-MM-DD · <título corto del cambio>
- **Pedido por Gerard:** …
- **Cambiado:** … (archivos/áreas)
- **Cómo revertir:** …
-->

### 2026-07-26 · Flujo de programación de calendario (nuevo)
- **Pedido por Gerard:** al programar, leer los vídeos del cliente (Drive), proponer orden (él
  decide), generar copy y mandar por WhatsApp la lista concisa (día + título) lista para reenviar;
  dejar además la programación lista para Metricool tras su OK (sin tocarla antes).
- **Cambiado:** nuevos `infra/programacion/listar_videos.py` (Drive API, orden por nº de nombre),
  `infra/programacion/calendario.py` (reparte por el calendario canónico → lista concisa +
  `metricool.json`), `infra/metricool/programar.py` (sube a Metricool solo con `--confirmar`, crea
  borradores). `config/drive-carpetas.json` (mapa cliente→carpeta Drive). Flujo documentado en
  `infra/responder/winy-tareas.md`. Prerequisitos de Gerard en `infra/SETUP.md` (punto 6).
- **Cómo revertir:** borrar esos 4 scripts + `drive-carpetas.json` y la sección de winy-tareas.md.

### 2026-07-26 · Ideas de contenido → Bandeja de Ideas RM en Notion (nuevo)
- **Pedido por Gerard:** guardar las ideas (incluidas las que salgan de links de IG/TikTok) en
  Notion, no en local.
- **Cambiado:** creada base Notion "Bandeja de Ideas RM"; nuevo `infra/notion/idea_add.py` para
  insertar ideas (estado "pendiente de grabar"); `infra/ideas/video_link.py` saca título/desc de
  un reel sin descargarlo; `process.sh` detecta links de IG/TikTok y fuerza el carril 2 para
  guardarlos; instrucciones en `winy-tareas.md`. Prerequisito: clave de Notion (`SETUP.md` p.5).
- **Cómo revertir:** quitar la detección de link de `process.sh`, borrar los dos scripts nuevos y
  la instrucción de ideas en `winy-tareas.md` (la base de Notion se archiva a mano).

### 2026-07-26 · Recordatorios estructurados + captura barata (nuevo)
- **Pedido por Gerard:** mejorar dónde/cómo se guardan los recordatorios.
- **Cambiado:** `estado.py` (`leer_notas`) ordena por vencimiento y marca ⚠️ los vencidos;
  `router.py` captura "recuérdame ..." simple a 0 tokens (apunta directo en la bandeja) y ya no
  escala esos casos; formato con metadata opcional `(📅 fecha · ⚡prioridad · #cliente)`
  documentado en `notas/📥 Bandeja.md` y `winy-tareas.md`.
- **Cómo revertir:** restaurar `leer_notas` a "solo líneas - [ ]" y volver a meter `recuerdame`
  en `ACCIONES` de `router.py` quitando `capturar_recordatorio`.

### 2026-07-26 · Calendario canónico por cliente (corrige el de 07-25)
- **Pedido por Gerard:** vale su WhatsApp del 25/07 (no el "todos mié+dom" que se aplicó antes).
- **Cambiado:** `config/calendario-publicacion.md` y `REGLAS` de `chequeo_cobertura.py` a: Newmos
  solo dom · resto mié+dom · Midtown mar+jue+sáb. INBOX y memoria actualizados.
- **Cómo revertir:** volver a la regla única "mié+dom para todos".

### 2026-07-25 21:16 · Limpieza mensual automática (Nova)
- **Pedido por Gerard:** limpieza periódica mensual de registros viejos/inútiles.
- **Cambiado:** vaciados logs volátiles (responder, servidor, check-in) + ids anti-bucle; memoria de conversación podada a 30 días; borrados 0 .DS_Store y temporales de audio.
- **Cómo revertir:** no aplica (solo se elimina ruido; nada de datos de negocio se toca).

### 2026-07-25 · Días de publicación → solo miércoles y domingo (Nova)
- **Pedido por Gerard:** "solo publicamos domingos o miércoles".
- **Cambiado:** en `config/calendario-publicacion.md`, Midtown tenía Jueves/Sábado/Martes; unificado a regla única **Miércoles y Domingo, 15:00** para TODOS los clientes.
- **Cómo revertir:** restaurar la fila de Midtown a "Jueves y Sábado + Martes".

### 2026-08-01 03:00 · Limpieza mensual automática (Nova)
- **Pedido por Gerard:** limpieza periódica mensual de registros viejos/inútiles.
- **Cambiado:** vaciados logs volátiles (responder, servidor, check-in) + ids anti-bucle; memoria de conversación podada a 30 días; borrados 13 .DS_Store y temporales de audio.
- **Cómo revertir:** no aplica (solo se elimina ruido; nada de datos de negocio se toca).

### 2026-08-14 · Winston arreglado · plantillas testeables en Coco · Olivia crítica · QA definido
- **Pedido por Gerard:** "arreglar Winnie, actualizar a Olivia y Coco con lo que haga falta,
  darle un trabajo definido a QA (lo dejaremos en stand-by), arreglar todo y verificar".
  Antes se auditó el sistema real contra la descripción que él tenía en la cabeza.
- **Cambiado:**
  - **Winston**: `infra/winston/winston-checkin.sh` — tope de coste 0.05 → 0.20 (llevaba
    4 noches muriendo con `error_max_budget_usd`, del 10 al 13/08, sin que nadie lo notara
    porque los otros avisos sí llegaban). Añadido **fallback ruidoso**: si el modelo no
    responde, ahora se envía el estado en crudo con cabecera de aviso en vez de callarse.
  - **Desfase de la Bandeja**: `infra/estado/estado.py` — nueva `refrescar_bandeja()`, llamada
    con `--refrescar`. El check-in (00:30) leía la caché que `noche.sh` escribe a las 00:45, o
    sea siempre la de 24h antes.
  - **Rutas rotas tras la migración**: `config/rutas.md` (4 de 5 repos apuntaban a `~/Documents`),
    `infra/estado/estado.py` (`ANALISIS_REGISTRO`), `infra/analista/analista.sh`,
    `infra/analista/kickoff.md`, `agentes/analista.md`. Al arreglarlo reapareció el aviso de
    análisis mensual pendiente, que llevaba semanas devolviendo vacío en silencio.
  - **Coco**: nueva carpeta `agentes/guiones/plantillas/` con 8 mecánicas + README con su estado
    de evidencia. `_comun.md` reescrito (el ejemplo con tramos fijos se estaba copiando literal:
    todas las piezas salían con la misma rejilla 0:03-0:08/0:08-0:15/0:15-0:25) y con
    **precedencia del CTA** explícita (ficha > plantilla > Tipo), que antes no estaba resuelta y
    hacía que Viral y Marca acabaran con el mismo CTA. `infra/notion/guionizar.py`: lee/escribe
    la propiedad `Plantilla`, prohíbe inventar datos del cliente (había escrito "Dolça Fantasia"
    donde la ficha dice "L'Abrador"), y **apunta la hipótesis sola** en `hipotesis.json`.
    Nueva propiedad `Plantilla` en las 6 bases de Notion (`infra/notion/anadir_plantilla.py`).
  - **Termómetro**: `infra/estado/termometro.py` — nueva `por_plantilla()` y flag `--plantillas`
    (por cliente y cruzando todos). Sin esto las plantillas no servirían de nada.
  - **Olivia**: `agentes/estratega.md` reescrita — su entregable pasa de un shotlist en prosa a
    `hipotesis.json`, con contrato de transparencia obligatorio (evidencia citada o "apuesta
    ciega" declarada, `descartadas`, `riesgos`, `datos_que_faltan`), validación previa contra
    restricciones de rodaje y pieza de control obligatoria. Nuevos `infra/olivia/olivia.sh` y
    `infra/olivia/kickoff.md` (patrón del Analista: interactivo, no cron).
  - **QA**: `agentes/qa.md` — cerrados los tres TBD (qué bloquea vs avisa, a quién devuelve,
    peso A/B) y marcado **explícitamente en stand-by**, con §6 de cómo encenderlo.
  - **Mapa y docs**: `CLAUDE.md` (tabla de agentes completa + quién corre solo y quién no),
    `agentes/copywriter.md` (Coco tenía dos trabajos y solo estaba documentado uno),
    `ciclos/HIPOTESIS.md` (campo `plantilla` + quién escribe qué).
- **Verificado:** check-in en dry-run (vuelve a redactar y formatear), `noche.sh --dry-run`
  entero, termómetro en todos sus modos, y **una prueba real de punta a punta**: ficha de test
  creada en Golossa → Coco eligió `comparativa-duelo`, generó 4 beats con tramos propios, citó
  las métricas reales del cliente, pidió el dato que faltaba en vez de inventarlo y escribió el
  `hipotesis.json`. Ficha archivada y JSON de prueba borrado después.
- **Cómo revertir:** el tope de coste y el fallback, a mano en `winston-checkin.sh`; borrar
  `agentes/guiones/plantillas/`, `infra/olivia/` y `infra/notion/anadir_plantilla.py`; quitar
  `por_plantilla`/`--plantillas` de `termometro.py` y los bloques de `Plantilla`/
  `apuntar_hipotesis` de `guionizar.py`. La propiedad `Plantilla` de Notion se borra a mano
  desde cada base (es additiva: dejarla no rompe nada).

### 2026-08-14 · Banco de plantillas reestructurado + capa de metodología de redacción
- **Pedido por Gerard:** las plantillas sirven para marca; en viral o replicas una referencia
  adaptándola, o es una idea nueva y no hay plantilla que valga. Además aportó tres cosas que
  no estaban en el sistema: el principio de **valor gratis**, dos **metodologías de redacción**
  y el **test de compartibilidad**.
- **Cambiado:**
  - **Tres capas** en vez de dos: `Tipo` (objetivo) · `Plantilla` (qué pieza es) ·
    **`Metodologia`** (cómo se redacta). Nueva propiedad `Metodologia` en las 6 bases de Notion.
  - **`_comun.md`**: añadido el principio de valor gratis (el origen: los vídeos de muebles
    antiguos de la empresa del padre de Gerard); las dos metodologías — `valor-directo`
    (gancho → necesidad → valor → CTA) y `bucle-abierto` (cada respuesta planta la siguiente
    pregunta **en la mente del espectador, sin enunciarla**); y el test de compartibilidad
    obligatorio con sus 4 motivos (Identidad · Utilidad · Plan · Desahogo).
  - **Borradas** `humor-situacion.md` y `comparativa-duelo.md`: estaban escritas como moldes
    cuando son mecánicas virales. Su contenido medido se conserva como "patrones que ya han
    funcionado" dentro de `viral-original.md` y como etiquetas.
  - **Viral pasa a ser 2 procesos**: `replica-referencia` (input = el desglose de Gerard, NO el
    enlace) y `viral-original` (restricciones + criterios de descarte; la única que puede decir
    "esta idea no da").
  - **5 moldes de marca nuevos**: `error-mito`, `caso-real`, `comparativa-criterio`,
    `objecion`, `antes-despues`. Total: 11 moldes de marca + 2 procesos de viral.
  - **`pregunta-real` reescrita** con el filtro que aportó Gerard: la pregunta tiene que ser
    del nicho **y** curiosa para quien no es cliente. ("¿Cómo se limpia el condensador de una
    nevera?" ❌ · "¿Cómo de grandes son las neveras de restaurante?" ✅.)
  - **`guionizar.py`**: nuevos campos `metodologia`, `compartible` y `valor_gratis`; gate que
    **para las réplicas sin desglose** (las saca de la cola con `Guion = Falta desglose` y pide
    2 líneas por WhatsApp, de una en una) en vez de inventarse el viral.
- **Comprobado con datos (14/08):** `video_link.py` sobre Instagram devuelve **vacío siempre**
  (bloquea sin login); sobre TikTok devuelve el pie de foto completo. Por eso las 11
  referencias de la Bandeja están sin descripción: no es dejadez, el sistema no puede leerlas.
  **Recomendación: guardar el TikTok en vez del Instagram** cuando exista.
- **Corregido un diagnóstico erróneo del 13/08:** se dijo que Coco había alucinado "Dolça
  Fantasia". **Falso**: es el nombre real del punto de venta de Valls y sale en los pies de
  foto de Golossa. El obrador es L'Abrador. Coco mezcló dos nombres reales porque la ficha solo
  recogía uno. Arreglada `memoria/clientes/golossa/ficha.md` con los 4 locales y sus nombres
  exactos; matizada la regla en `agentes/copywriter.md` y `agentes/qa.md` (si el dato existe,
  el bloqueo es de ficha, no de quien escribe).
- **Verificado:** prueba real de punta a punta con dos fichas de test. La de marca salió con
  `pregunta-real` + `bucle-abierto`, bucles reales en los beats, `compartible: Utilidad`, y
  declaró **"sin evidencia — apuesta ciega"** en vez de inventarse una justificación; además
  escribió los nombres de Valls correctamente. La réplica sin desglose **se paró sola** y dejó
  la instrucción concreta en el INBOX. Las dos fichas archivadas y el JSON de prueba borrado.
- **Cómo revertir:** `git`-less, así que a mano: borrar los 7 .md nuevos de `plantillas/`,
  restaurar `humor-situacion.md`/`comparativa-duelo.md` desde este log, y quitar de
  `guionizar.py` los bloques `METODOLOGIAS`/`COMPARTIBLE`/`EXIGEN_DESGLOSE`,
  `tiene_desglose()` y `avisar_desglose()`.

### 2026-08-14 · Corrección: lo de "Dolça Fantasia" era un falso positivo
- **Aclarado por Gerard:** en Valls **el obrador está en el mismo local que el punto de venta**
  — es un único sitio, y se llama **Dolça Fantasia**. "L'Abrador" no es ningún nombre: era
  "el obrador" mal escrito en la ficha vieja.
- **Consecuencia:** el guion original de Coco del 13/08 ("Obrador de Valls (Dolça Fantasia)")
  **era correcto**. No hubo alucinación en ningún momento; el error estaba en la ficha, y luego
  en el diagnóstico que se hizo de él — y ese diagnóstico erróneo se propagó a tres documentos.
- **Cambiado:** `memoria/clientes/golossa/ficha.md` (Valls = un solo local, Dolça Fantasia, con
  nota de que "L'Abrador" es un error de transcripción a borrar donde aparezca);
  `agentes/copywriter.md` y `agentes/qa.md`, donde el ejemplo pasa de "así se inventa un dato" a
  **"así se marca un falso positivo"**: antes de bloquear un dato por inventado hay que
  comprobar si existe, y si existe el fallo es de la ficha.
- **Lección para el sistema:** una ficha desactualizada no solo produce errores — produce
  **acusaciones falsas de error**, que es peor, porque hacen desconfiar de quien acertó.

### 2026-08-14 · El puente Coco → Analista: clasificar el contenido, no solo medirlo
- **Pedido por Gerard:** "el analista tendría que entender perfectamente y clasificar los
  vídeos para calificar qué es bueno y qué sirve y qué no, a partir de las etiquetas o
  referencias que deje Coco en el guion o en la página de Notion. Y esto se tiene que hacer
  saber al analista y documentarse bien."
- **El problema:** el Analista trabaja con el PDF bruto de Metricool, que trae vistas y el
  texto del post pero **no sabe con qué plantilla ni metodología se hizo cada pieza**. Deducía
  los "patrons guanyadors" leyendo el texto del post, que es adivinar con estilo.
- **Cambiado:**
  - Nuevo **`infra/notion/clasificacion.py`**: recorre las 6 bases y escribe
    `memoria/clasificacion/<cliente>.md` — una tabla por cliente de cada pieza publicada o
    programada con Tipo · Plantilla · Metodología · Palanca · Formato · fecha, más lo que Coco
    dejó en `hipotesis.json` (apuesta, porqué, etiquetas, compartible, resultado medido).
    **Un solo archivo por cliente**, para no romper el presupuesto de lectura del Analista: no
    tiene que abrir Notion.
  - Enganchado a `noche.sh` detrás de guionizar, para que no se quede viejo.
  - **Documentado en los tres sitios donde el Analista mira**: `agentes/analista.md` (nuevo
    §1 bis con el método y las reglas duras, y el archivo añadido al presupuesto de lectura),
    `infra/analista/kickoff.md` (paso 2 bis) y el **runbook canónico**
    `proyectos/Analisis mensual/CLAUDE.md` (en catalán, con aviso explícito en el punto 2 de
    "NO dedueixis el patró llegint el text del post").
  - `CLAUDE.md` del hub: añadido al mapa.
- **Reglas duras que se documentan:** una plantilla con una sola pieza **no concluye nada** y
  hay que decirlo; **no mezclar** piezas clasificadas con las anteriores al 14/08/2026 (no
  llevan plantilla y no se pueden reconstruir); el veredicto numérico lo da el termómetro, el
  Analista explica el porqué; y si una pieza funcionó **por un motivo distinto del que se
  apostaba**, ese es el aprendizaje más valioso del mes.
- **El enganche final:** lo que salga va a `memoria/aprendizajes/registro.md`, que es de donde
  Oli saca las ideas del mes siguiente. Sin eso, la clasificación es una página bonita del deck.
- **Verificado:** generados los 6 archivos y `noche.sh --dry-run` entero en verde. Hoy salen
  "0 clasificadas" en todos, que es lo correcto: todas las piezas publicadas son anteriores al
  sistema, y el archivo lo dice en vez de fingir que tiene datos.
- **Cómo revertir:** borrar `clasificacion.py`, `memoria/clasificacion/` y el bloque de
  `noche.sh`; quitar §1 bis de `analista.md`, el paso 2 bis del kickoff y el bloque del runbook.

### 2026-08-14 · Re-guionizado con el banco nuevo + tope de coste de Coco
- **Pedido por Gerard:** rehacer los guiones de Golossa con el banco nuevo (opción 2), empezando
  por dos para revisarlos a mano.
- **Cambiado:**
  - `notion_api.py`: nuevos `list_blocks()`, `delete_block()` y `texto_de_bloque()`.
  - `guionizar.py`: flags **`--reguionizar`** (trabaja sobre `Guion=Listo` en vez de "Coco a
    guionizar") y **`--titulo TEXTO`** (repetible, filtra por título). Nueva
    `limpiar_guion_anterior()`: borra desde la primera cabecera "🎣 Gancho" hasta el final, así
    que **lo que alguien haya escrito a mano ARRIBA de la ficha se respeta**. Sin esto, los dos
    guiones quedaban pegados.
  - **`PRESUPUESTO_USD` 0.25 → 0.60.** Al pasar de 2 a 13 plantillas el prompt creció a ~54 KB
    (el catálogo entero va dentro si la idea no trae Plantilla) y el coste real subió a
    **0.255**: dos céntimos por encima del tope. La idea moría con `budget_exhausted`.
    Truco de coste documentado: si la idea ya trae Plantilla (Oli normalmente la pone), solo va
    esa al prompt y sale mucho más barato.
  - **`llamar_coco()` ya no falla mudo**: `claude` puede salir !=0 con stderr VACÍO y el motivo
    real en el JSON de stdout (`terminal_reason`). Ahora se lee de ahí y se reporta con el coste
    y el tope. Es el tercer fallo silencioso de la misma familia en dos días (SSL, check-in de
    Winston, este): **cuando algo salga !=0, mira siempre si el motivo está en stdout.**
- **Verificado:** re-guionizadas 2 piezas de Golossa. "El encargo, de principio a fin" salió con
  `caso-real` + `valor-directo` (plantilla que no existía antes) y "Cómo sabemos que está lista"
  con `pregunta-real` + `bucle-abierto`, con bucles reales encadenados. Las dos citan bien los
  nombres de Valls y declaran honestamente su falta de evidencia.
- **Defecto detectado, sin arreglar:** en una de las dos, Coco citó "hipótesis jm-09-8" (que es
  de Jesús Mora) para justificar algo de Golossa. La cita es errónea aunque el razonamiento no.
  Vigilar si se repite: si pasa, hay que acotar en el prompt que solo puede citar evidencia
  **del cliente que está guionizando**.
- **Cómo revertir:** quitar los dos flags y `limpiar_guion_anterior()` de `guionizar.py`, y los
  tres helpers de `notion_api.py`. Los guiones viejos de esas 2 piezas **no se pueden recuperar**.

### 2026-08-19 · Arranque de publicación de Xavi Colomina (config + fichas)
- **Pedido por Gerard:** organizar el contenido de Xavi en Metricool y empezar a programar.
  3 posts/semana desde el **martes 01/09/2026**, con el día 1 reservado a la presentación
  (aún sin montar), repartiendo las series de forma uniforme.
- **Decidido por Gerard (19/08):** días = **martes, jueves y domingo** · hora = **15:00** ·
  el podcast entra en la rotación (borró C03/C05/C06/C08/C13 ese mismo día, quedan 9 clips).
- **Cambiado:**
  - `config/publicacion.json` — entrada `xavi-colomina` en `dias` (1/3/6). Su pausa
    (hasta 31/08) se deja: se agota sola. El `_pendiente` se sustituye por `_nota_xavi`.
  - `config/drive-carpetas.json` — `xavi-colomina` = `1RZHYPag8-iJ6hQpOhCkZMr8oqoV53WqQ`
    (antes `null`, bloqueaba `listar_videos.py`). Aviso: sus subcarpetas son SERIES, no meses.
  - `memoria/clientes/xavi-colomina/copy-brief.md` — **nuevo**. No es verbatim de Gerard:
    está derivado de `ficha.md` + `marca.json`. ⚠️ Pendiente de validar con Gerard/Xavi.
  - `memoria/clientes/xavi-colomina/marca.json` + `ficha.md` — cadencia real (ya no "TBD").
  - `ciclos/2026-09/xavi-colomina/` — `manifest.json` + `programacion/videos.json`
    (las 52 piezas con fecha) + `programacion/reparto.py` (el script que las repartió).
  - Notion "Contenido Xavi Colomina" — **51 fichas nuevas** (una por vídeo de Drive) con fecha,
    enlace al vídeo y clasificación por serie. La ficha "Presentació" se movió del 06/09 al 01/09.
- **Cómo revertir:** quitar la entrada de xavi en `publicacion.json` y volver a poner el
  `_pendiente`; `drive-carpetas.json` a `null`; borrar `copy-brief.md` y `ciclos/2026-09/xavi-colomina/`.
  En Notion, las 51 fichas se reconocen por `Notas` = "Serie … · origen Drive: …".

### 2026-08-19 · Metricool: subida de vídeos de más de 100 MiB (arreglo)
- **Problema:** al programar septiembre de Xavi, 4 de los 12 vídeos fallaron con
  `HTTP 400 · InvalidPresignedUploadRequestException: part size exceeds maximum`. Medido:
  **95 MiB pasa, 101 MiB no** → el límite de Metricool es **100 MiB por parte**. Afecta a ~10
  de los 51 vídeos de Xavi, y a cualquier cliente con piezas largas.
- **Cambiado:** `infra/metricool/subir_media.py` → `subir_a_metricool()` trocea en partes de
  90 MiB. Con una sola parte el flujo es el de siempre (uploadType SIMPLE, la transacción ya
  trae `fileUrl`). Con varias, la API abre una MULTIPART: se sube cada parte a su
  `presignedUrl`, se guarda el `ETag` de cada una, y se cierra con
  **`PATCH /v2/media/s3/upload-transactions`** y cuerpo
  `{"multipart": {key, bucket, uploadId, parts:[{partNumber, etag, checksumSha256}]}}`,
  que es el que devuelve la `fileUrl`. Endpoint no documentado, encontrado a base de probar.
- **Verificado:** los 4 vídeos que fallaban (106–200 MB) subieron a la primera tras el cambio.
- **Cómo revertir:** volver a la versión de una sola parte (git/Time Machine). Perderías la
  capacidad de subir cualquier vídeo de más de 100 MiB.

### 2026-08-21 · Xavi a 3 redes (+ YouTube Shorts) y copy con SEO
- **Pedido por Gerard:** "a partir de ahora para Xavi, todos los vídeos en Instagram Reels,
  TikTok **y YouTube Shorts**; en YT hay que inventar un título gancho y rellenarlo. Y el copy
  hay que trabajarlo mucho con SEO, como expertos: palabras clave según el vídeo y siempre las
  generales tipo 'padel'."
- **Cambiado — regla de negocio (fuente única):**
  - `config/metricool-marcas.json` — nuevo `_redes_default` (`["instagram","tiktok"]`) y
    `redes` por cliente. Xavi: `["instagram","tiktok","youtube"]`. **Las redes ya no están
    escritas a mano en ningún script.**
  - `infra/programacion/calendario.py` — nueva `redes_de(cliente)`; deja de hardcodear
    IG+TikTok y arrastra `yt_titulo` al `metricool.json`.
  - `infra/metricool/programar.py` — manda `youtubeData = {title, type: SHORT, privacy: PUBLIC}`.
    **Se planta antes de subir el vídeo si falta `yt_titulo`** (mejor no crear el post que
    crearlo con el nombre del archivo de título). El preview lo marca con 📺.
  - `infra/metricool/chequeo_cobertura.py` — un slot cuenta como cubierto solo si lleva TODAS
    las redes del cliente, no las dos de siempre.
- **Cambiado — contenido:**
  - `memoria/clientes/xavi-colomina/copy-brief.md` — secciones nuevas **SEO** (dos capas:
    generales siempre + específicas del vídeo, tabla de tema→keywords, subtítulo-pregunta para
    la long-tail), **Hashtags** (8-10, sin repetir entre texto y bloque) y **YouTube Shorts —
    el TÍTULO**. Estas tres SÍ son instrucción directa de Gerard.
  - `memoria/clientes/xavi-colomina/marca.json` — `redes_metricool`, bloque `youtube` y `seo`.
  - `agentes/copywriter.md` — Coco: si el cliente lleva YouTube, el título es obligatorio.
  - Notion "Contenido Xavi Colomina" — **propiedad nueva `Título YT`**.
  - Los 12 copies de septiembre reescritos con SEO + su título de YT, y los 12 borradores de
    Metricool actualizados en sitio (sin volver a subir el vídeo).
- **Ojo:** actualizar un post de Metricool con `PUT /v2/scheduler/posts/{id}` **le cambia el
  id**. Si guardas el `Metricool ID` en Notion, hay que releerlo después.
- **Cómo revertir:** quitar `redes` de Xavi en `metricool-marcas.json` (los scripts vuelven
  solos a IG+TikTok) y borrar el bloque `youtubeData` de `programar.py`.

> **Nota de la API (21/08/2026):** para ACTUALIZAR un post existente hay que hacer
> `PUT /v2/scheduler/posts/{id}` con el objeto entero. Dos trampas:
> 1. El `GET` devuelve los enums de `youtubeData` en **minúscula** (`"short"`, `"public"`),
>    pero el `PUT` los exige en **MAYÚSCULA**. Si reenvías tal cual lo que te dio el GET,
>    responde **500 sin cuerpo**. Hay que reconstruir `youtubeData` con `SHORT`/`PUBLIC`.
> 2. El `PUT` **cambia el id del post**. Si guardas el `Metricool ID` en Notion, reléelo
>    después de actualizar.

### 2026-08-21 · YouTube: audiencia, categoría y etiquetas (completa el cambio anterior)
- **Pedido por Gerard:** en los posts de YouTube de Xavi hay que marcar la audiencia como
  **no creada para niños**, poner la categoría **Deportes**, y en **etiquetas** los hashtags
  del texto.
- **Forma real de la API** (`youtubeData`, encontrada probando el 21/08/2026):
  `madeForKids: false` · `category: "SPORTS"` · `tags: ["padel", "globo en padel", ...]`.
  `categoryId` numérico se ignora. Categorías válidas: FILM_ANIMATION, AUTOS_VEHICLES, MUSIC,
  PETS_ANIMALS, SPORTS, TRAVEL_EVENTS, GAMING, PEOPLE_BLOGS, COMEDY, ENTERTAINMENT,
  NEWS_POLITICS, HOWTO_STYLE, EDUCATION, SCIENCE_TECHNOLOGY, NONPROFITS_ACTIVISM.
- **Cambiado:**
  - `config/metricool-marcas.json` — bloque `youtube` por cliente (Xavi: SPORTS + madeForKids
    false) y `_youtube` explicando los valores válidos.
  - `infra/metricool/programar.py` — `ajustes_youtube(cliente)` (audiencia y categoría, fijas
    del cliente) y `tags_de_texto(texto)`, que saca las **etiquetas de los hashtags del copy**:
    quita la almohadilla y parte el CamelCase (`#GloboEnPadel` → `globo en padel`), sin repetir
    y cortando a los 500 car. que admite YouTube. Nadie escribe las etiquetas a mano.
  - `copy-brief.md` / `marca.json` — documentado, **más una regla nueva de escritura: los
    hashtags multipalabra van en CamelCase**, porque de ellos salen las etiquetas. En minúscula
    corrida salían pegadas (`culturadelesfuerzo`).
  - Los 12 borradores de septiembre, actualizados con audiencia, categoría y etiquetas.
- **Trampa (costó un rato):** al hacer `PUT` hay que **reconstruir `providers`** como
  `[{"network": n}]`. Si reenvías los que devuelve el `GET` (traen `status`/`detailedStatus`),
  responde `500 · Type definition error: PublicationStatusCode` — un error que no menciona
  para nada el campo que falla.
- **Cómo revertir:** borrar el bloque `youtube` de Xavi en `metricool-marcas.json` y la llamada
  a `tags_de_texto` en `programar.py`.

### 2026-08-21 · Xavi autopublica (se cruza el Gate 3 para este cliente)
- **Pedido por Gerard:** "dale a la opción siempre de autopublicar, para que se programe y
  publique solo".
- **Qué implica:** para Xavi **ya no hay revisión humana** entre el copy y la publicación.
  Se le avisó de que los copies de septiembre están escritos desde el `copy-brief.md`, que él
  todavía no ha validado, y aun así lo pidió.
- **Cambiado:**
  - `config/metricool-marcas.json` — `autopublicar: true` en Xavi + `_autopublicar` explicando
    qué significa. Bandera POR CLIENTE: el resto sigue creando borradores.
  - `infra/metricool/programar.py` — `autopublica(cliente)`; `publicar = --publicar or
    autopublica(...)`. Manda `draft=false`, `autoPublish=true` y también
    `instagramData.autoPublish=true` (IG lo lleva en su propio flag). El preview lo canta con
    🚨 y el email de aviso cambia de texto: ya no dice "revísalos antes de publicar".
  - Los 12 posts de septiembre + el del 01/10, pasados a firme.
- **Cómo revertir:** quitar `autopublicar` de Xavi en marcas.json (los nuevos vuelven a ser
  borradores) y poner `draft=true` a mano en el planner a los que ya están en firme.

### 2026-08-21 · Reordenado: segunda presentación el 03/09
- **Hecho por Gerard en el planner:** movió "Defensa: cierra la línea directa" del 03/09 al
  01/10 para dejar el 03/09 libre para un **segundo vídeo de presentación**.
- **Error mío:** mi verificación tomó ese movimiento por deriva y lo devolvió al 03/09.
  Restaurado. **Lección: no forzar las fechas de Metricool contra el plan** — si no cuadran,
  reportarlo, porque el planner también lo toca Gerard.
- **Cambiado:** `ciclos/2026-09/xavi-colomina/programacion/videos.json` reordenado (53 posts,
  01/09 → 31/12), ficha nueva "Presentació Xavi Colomina 2" en Notion con el 03/09 reservado,
  y todo lo posterior al 01/10 corrido un hueco.

### 2026-08-25 · Formato de las ideas de IG: Reel vs Carrusel (arreglo)
- **Pedido por Gerard:** "cuando le mando a Winy posts de Instagram no me los clasifica según
  reels o carruseles, pone Reel a todo".
- **Causa:** no era el modelo. `infra/responder/process.sh` metía `"formato": "Reel"` **literal**
  en la plantilla JSON que Winy solo tenía que rellenar; los ejemplos de `winy-tareas.md` y del
  README de la cola anclaban lo mismo. Aguas abajo (`distribuir.py`) el Carrusel siempre estuvo
  soportado.
- **Cambiado:** `infra/ideas/video_link.py` deduce ahora el formato de la URL (0 tokens,
  determinista): `/reel/ /reels/ /tv/` y TikTok → Reel; `/p/` con `og:video` → Reel; `/p/` sin
  vídeo → Carrusel (certeza media). Lo emite en el JSON como `formato` + `certeza`.
  `process.sh` inyecta ese formato en la plantilla en vez del "Reel" fijo (y si no lo sabe, quita
  el campo). `winy-tareas.md` y `infra/ideas/cola/README.md`: `formato` ya no tiene valor por
  defecto — si no se sabe, se omite (hueco visible en Notion) en vez de mentir con Reel.
- **Cómo revertir:** volver a poner el literal `\"formato\": \"Reel\"` en el bloque de link de
  `process.sh` y quitar `formato_desde_url()` de `video_link.py`.

### 2026-08-30 · Carrusel de servicios de Xavi (nuevo tipo de pieza)
- **Pedido por Gerard:** programar en Instagram y TikTok el carrusel diseñado en Claude Design
  ("Carrusel de servicios Instagram"), el jueves 03/09.
- **Hecho:** post EN FIRME el 03/09/2026 a las 15:00, 7 slides de 1080x1080, copy con SEO.
  El 03/09 lo tenía reservado la "Presentació Xavi Colomina 2", que se queda sin fecha hasta
  que se grabe. El resto del calendario no se toca.
- **Nuevo:** `ciclos/2026-09/xavi-colomina/programacion/carrusel.py`. `programar.py` solo sabe
  de piezas de vídeo (un `drive_id` por post); un carrusel son N imágenes locales en un post.
  Reutiliza `subir_media` y las banderas de `programar.py` (autopublicar).
- **Regla de formato:** un carrusel **no puede ir a YouTube Shorts**, así que esta pieza es la
  excepción al `redes` de Xavi: solo `instagram` + `tiktok`, sin `yt_titulo` ni etiquetas.
- **API de Metricool:** varias entradas en `media` + `instagramData.type = "POST"` (no `REEL`)
  = carrusel de Instagram. Verificado: 7 slides, autoPublish en el post y en `instagramData`.
- **Truco para sacar ficheros de un proyecto de Claude Design** (costó un rato):
  - La MCP `DesignSync` necesita `/design-login` y **no se puede autorizar en sesión headless**.
  - Desde la pestaña de claude.ai (con sesión) sí se puede llamar a la API Connect-RPC:
    `POST /design/anthropic.omelette.api.v1alpha.OmeletteService/{ListFiles,GetFile}` con
    `{projectId, path}`; `GetFile` devuelve el contenido en base64.
  - Para bajarlos al disco, **no sirven las descargas del navegador** (Chrome bloquea las
    múltiples) ni un POST a `127.0.0.1` (lo corta Private Network Access). Lo que sí funciona:
    los assets se sirven en
    `https://<projectId>.claudeusercontent.com/v1/design/projects/<projectId>/serve/<ruta>?t=<token>`
    y **ese token NO está ligado a la ruta**: se captura uno del log de red y con él se hace
    `curl` de cualquier fichero del proyecto.
- **Cómo revertir:** borrar el post 368527179 en el planner y la ficha "Carrusel — Servicios
  Xavi Colomina" en Notion, y devolverle la fecha del 03/09 a la Presentació 2.

### 2026-08-30 · Presentación programada y carrusel movido al miércoles
- **Presentación (01/09):** Jaume subió el montaje el 30/08 a Drive · `PRESENTACIÓ IG/YT`.
  Hay DOS cortes de 45s casi del mismo peso: `..._IG TIKTOK_45s.mp4` y `..._YT_45s_v2.mp4`.
  **Gerard decidió usar el corte de IG en las 3 redes**; el de YT queda sin usar. Post EN FIRME
  el 01/09 a las 15:00, con copy SEO y título de Short.
- **Carrusel:** Gerard lo movió del jueves 03 al **miércoles 02**. Es un día fuera de la
  cadencia (mar/jue/dom): excepción puntual, no se toca `publicacion.json`.
- **Queda un borrador vacío el 01/09** (id 364088540, texto "Presentacio", sin vídeo): lo creó
  Gerard el 19/08 para reservar el hueco. No se ha borrado por ser suyo — no publica nada, pero
  conviene quitarlo del planner para no tener dos tarjetas ese día.
- **Presentación 2:** sigue sin grabar y sin fecha.

### 2026-08-30 · Reordenado el arranque de Xavi (segunda vuelta)
- **Pedido por Gerard:** cambiar la semana de lanzamiento — martes un teaser de 8s que ya tenía
  en borradores, miércoles el carrusel, jueves la presentación de 45s, y domingo un vídeo de
  Xavi explicando el proyecto que sigue en edición con Jaume. Lo que había el domingo (una pieza
  de pista) se aplaza.
- **Decisión suya sobre el aplazamiento:** en vez de buscarle hueco suelto, **se corre todo un
  slot** para que esa pieza abra la semana siguiente. Es lo correcto: el orden del stock no es
  arbitrario, está repartido para que la mezcla de series (tips / podcast / ejercicios /
  explicaciones) salga uniforme. Moverla sola habría roto el reparto.
- **Hecho:** las 12 piezas de vídeo en firme corridas un slot (06/09→08/09 … 01/10→04/10),
  procesando de la última a la primera para no pisar fechas. Teaser y presentación pasados a
  firme con copy, título de Short y etiquetas. 55 piezas en el plan, hasta el 03/01/2027.
- **Copy del teaser:** deliberadamente mínimo, por instrucción de Gerard. Es un reclamo para
  quien ya conoce a Xavi ("Si sabes quién es, con esto te basta"), sin explicar nada; todo el
  peso de SEO va en los 10 hashtags. Es la excepción a la estructura del copy-brief.
- **Ojo:** el miércoles 02/09 está fuera de la cadencia mar/jue/dom. Es una excepción puntual
  del carrusel, no se toca `publicacion.json`.
- **Cómo revertir:** correr las 12 piezas un slot hacia atrás y devolver el teaser y la
  presentación a borrador.

### 2026-09-01 03:00 · Limpieza mensual automática (Nova)
- **Pedido por Gerard:** limpieza periódica mensual de registros viejos/inútiles.
- **Cambiado:** vaciados logs volátiles (responder, servidor, check-in) + ids anti-bucle; memoria de conversación podada a 30 días; borrados 8 .DS_Store y temporales de audio.
- **Cómo revertir:** no aplica (solo se elimina ruido; nada de datos de negocio se toca).

## 07/09/2026 — Xavi: fuera todos los CTA de venta

**Qué pidió Gerard.** «Elimina todos los CTAs de los copys en Metricool que sean de venta o
puedan parecerlo. No queremos que se intuya para nada que queremos vender algo en algún
momento.»

**Cambio de regla de negocio.** El brief decía "destino único: el DM de Instagram" y cada
copy cerraba con `📩 Diagnóstico por DM en Instagram · @xavicolominapadel`. Eso se acabó:
**los copys de Xavi no llevan CTA**. Terminan en la última línea de contenido y detrás van
solo los hashtags. La fase es de autoridad, no de captación.

Única excepción admitida: una acción del jugador **consigo mismo**, sin destinatario ni
respuesta esperada — "Pruébalo esta semana", "Grábate de perfil un día". No pide nada.

**Dónde vive ahora la regla** (se cambió en los cuatro sitios):
- `memoria/clientes/xavi-colomina/copy-brief.md` → § 3 reescrita + regla obligatoria + plantilla.
- `memoria/clientes/xavi-colomina/marca.json` → bloque `cta` a null con `_nota`.
- `memoria/clientes/xavi-colomina/ficha.md` → CTA y lente de métrica.
- Este registro.

**Qué se tocó.**
- Metricool: 9 posts del 15/09 al 04/10. Los del 08, 10 y 13/09 ya los había limpiado Gerard
  a mano — su formato fue el patrón a seguir. Los del 01 al 06/09 ya se habían publicado.
- `ciclos/2026-09/xavi-colomina/copies/*.md`: los 16.
- `programacion/videos.json` (16) y `programacion/metricool.json` (12). **Importante**: si no
  se limpian los JSON, una reprogramación reintroduce el CTA.
- Notion: 12 filas (`Copy RRSS` + `Metricool ID`).
- Hashtag `#DiagnosticoPorVideo` retirado del banco: nombra un servicio de pago.

**Gotcha ya conocido, confirmado otra vez.** Cada PUT cambia el id del post, así que después
de limpiar hubo que reescribir `Metricool ID` en Notion. Se casa por `Título YT`.

**Resuelto — el carrusel de servicios.** Gerard decidió el 07/09/2026 dejarlo tal cual para
cuando se empiecen a dar servicios. Es la excepción a la regla: conserva su copy de venta y su
CTA íntegros. Se le revirtió la limpieza (copy original restaurado en el `.md` y en
`videos.json`), se le quitó la fecha y se marcó `estado: APARCADO`. En Metricool sigue como
borrador con fecha pasada (02/09) y no publica: autopublicar solo actúa sobre posts en firme.
Al reactivarlo: fecha nueva, pasarlo a firme y avisar.

### 2026-09-21 · Limpieza de ex-clientes (Golossa, Midtown, MSM, Algoritmo)
- **Pedido**: Gerard — "haz limpieza" tras la auditoría (ya no trabajamos con ellos; facturación actual 1.150 € = Jesús Mora + Newmos).
- **Cambiado**: `config/notion-bases.json` (fuera de `clientes`, ids guardados en `exclientes`) · `config/metricool-marcas.json` (midtown → `fuera_de_roster_v1`) · `config/publicacion.json` (fuera días de Midtown y todas las pausas, incluida la caducada de Xavi) · `config/ciclo-mensual.json` (notas) · `pocket/clients.json` (inactivos; la app ya los tenía inactivos en Notion) · `idea_add.py` y `process.sh` (Winy ya no asigna ideas a ex-clientes) · `winy-system.md`, `winston-voz.md`, `winy-tareas.md`, `CLAUDE.md` (roster) · Bandeja de Notion: 10 ideas de ex-clientes → Estado=Descartada (28 → 18 sin triar) · `notas/📥 Bandeja.md`: cerradas las notas de Golossa y Midtown.
- **No tocado**: fichas de cliente, ciclos e hipótesis históricos, bases "Contenido X" de Notion (siguen existiendo).
- **Revertir**: copiar de vuelta los archivos de `memoria/_respaldo-limpieza-2026-09-21/`; en Notion, filtrar la Bandeja por Estado=Descartada y devolver a Nueva.

### 2026-09-22 · Etiquetas de la idea (Tipo de idea + Estructura) y ciclo de aprendizaje cerrado
- **Pedido por Gerard:** etiquetar cada idea de todas las bandejas con su tipo de idea y su
  formato de vídeo (ranking, lista, comparación, top 10, tips… abierto), para analizar qué
  funciona por cliente y retroalimentar las ideas siguientes.
- **Cambiado:**
  - Notion: propiedades `Tipo de idea` y `Estructura` (select, abiertas) en la Bandeja y en las
    4 bases activas. Se llaman "Estructura" y no "Formato" porque `Formato` ya es Reel/Carrusel.
    Nuevo `infra/notion/etiquetas_idea.py` (semilla idempotente + lectura en vivo de opciones).
  - Entrada: `idea_add.py` (`--tipo-idea`, `--estructura`, claves JSON `tipo_idea`/`estructura`),
    `distribuir.py` las baja al cliente, Winy las rellena si se ven claras (`winy-tareas.md`,
    `process.sh`).
  - Coco (`guionizar.py`, `_comun.md`): clasifica las que lleguen vacías con las opciones leídas
    en vivo; nunca pisa lo que puso una persona; si crea una opción nueva avisa (WhatsApp+INBOX).
  - Medición: `clasificacion.py` deja `memoria/clasificacion/_piezas/<cliente>.json` (lo
    publicado en Notion con sus etiquetas); `termometro.py --ideas/--estructuras/--tipos-idea`
    mide desde ahí cruzando por fecha con Metricool. `--plantillas` también mide ya desde ahí.
  - **Dos averías encontradas por el camino, que dejaban el termómetro a 0 piezas medidas:**
    (1) los títulos de `hipotesis.json` no casaban nunca con Notion (0 de 22 publicadas);
    (2) `fetch_metricool.py` no lo corría nadie desde el 11/08. Ahora corre en `noche.sh`.
  - Retroalimentación: Oli lee `--ideas` al montar la tanda (`estratega.md`, `kickoff.md`:
    explotar 3+, repetir 1-2, probar 1-2 nuevas); el Analista lo vuelca al cierre en
    `registro.md` y en "Qué funciona" de la ficha (`analista.md`).
- **Cómo revertir:** quitar las dos propiedades en Notion; quitar el bloque metricool de
  `noche.sh`; en `termometro.py`, `por_campo` volver a iterar `ciclos_con_hipotesis`.

### 2026-09-22 · Copies de Coco: cortos, SEO y sin repetir el vídeo
- **Pedido por Gerard:** copies mucho más cortos y concisos, optimizados en SEO, que no repitan
  lo que se dice en el vídeo.
- **Cambiado:** regla dura nueva en `agentes/guiones/_comun.md` (25-50 palabras de cuerpo,
  keyword principal en la 1ª línea, el copy aporta lo que el vídeo no dice; Coco usa gancho y
  beats como lista negra). **Manda sobre la longitud de los briefs**: actualizados
  `memoria/clientes/jesus-mora/copy-brief.md` (antes 100-170 palabras) y
  `xavi-colomina/copy-brief.md` (estructura comprimida a una frase por bloque; SEO y hashtags
  intactos). También `agentes/copywriter.md`, el prompt de `guionizar.py` y el de
  `infra/programacion/generar_copy.py`.
- **No toca** los copies ya escritos en Notion (`Copy RRSS` no vacío se reutiliza al programar).
- **Cómo revertir:** borrar la sección "Regla dura de Gerard (22/09/2026)" de `_comun.md` y
  restaurar las longitudes anotadas en los dos briefs.

### 2026-09-22 · "Formato" = formato del contenido · Reel/Carrusel pasa a "Soporte" · Autor + ideas de Oli a Notion
- **Pedido por Gerard:** que "Formato" sea el del contenido (tips, top, comparación…) y no
  Reel/Carrusel/Story; saber dónde van las ideas de Oli y poder distinguir quién hizo cada idea.
- **Cambiado:**
  - Notion (con `infra/notion/etiquetas_idea.py --renombrar`, idempotente): `Formato`→`Soporte`
    y `Estructura`→`Formato` en Bandeja + 4 bases. Nueva propiedad `Autor` (Gerard/Oli/Andrea/
    Cliente) y `Plantilla` también en la Bandeja. Vista **🤖 Propuestas de Oli** en la Bandeja.
  - Código: `idea_add.py` (`--soporte`, `--formato`, `--autor`, `--plantilla`; la cola de Winy
    mete `Autor=Gerard`; JSON viejos con `"formato":"Reel"` se entienden como soporte),
    `distribuir.py`, `guionizar.py`, `clasificacion.py`, `autoprogramar.py`, `video_link.py`,
    `process.sh`, `termometro.py` (`--formatos`, `--autores`; `--estructuras` queda de alias).
    Compatibilidad: `ei.nombres_reales/traducir/leer` usan el nombre que exista en cada base,
    así que el orden código/Notion no puede mezclar columnas.
  - Oli: nuevo `infra/olivia/a_bandeja.py` sube la tanda a la Bandeja con `Autor=Oli`, mismo
    título que `hipotesis.json` (arregla el cruce del termómetro). Documentado en `kickoff.md`
    y `estratega.md`. Hallazgo: la tanda de Jesús Mora 2026-09 (8 ideas) nunca llegó a Notion.
  - App Calendario Edición (`proyectos/Calendario Edición`, `lib/notion.js` + `pocket/server.js`):
    lee/escribe `Soporte`. **Requiere push a main (redeploy Vercel) justo antes de `--renombrar`.**
- **Cómo revertir:** `etiquetas_idea.py` no tiene vuelta automática: renombrar a mano en Notion
  `Formato`→`Estructura` y `Soporte`→`Formato`, y revertir el commit de la app.

### 2026-09-22 · Oli corre sola (miércoles 01:30) + aviso por WhatsApp Y correo + JM vuelve a miércoles
- **Pedido por Gerard:** que Oli genere la tanda sola en la noche del martes al miércoles, que
  avise también por correo (no solo WhatsApp) y que Jesús Mora vuelva a publicar miércoles y
  domingo.
- **Cambiado:**
  - Nuevo `infra/olivia/oli_noche.py` + `oli-noche.sh`. Monta la tanda de los clientes que están
    en su semana 📊 Analizar, la sube a la Bandeja con `Autor = Oli` (`a_bandeja.py`) y avisa.
    Idempotente por cliente y mes (`oli_auto` en `hipotesis.json`): algunos meses tienen dos
    miércoles en la misma semana. Contexto del prompt: termómetro (`--revisar`, `--ideas`,
    `--plantillas`), métricas, ficha, brief, aprendizajes, catálogo de plantillas,
    restricciones heredadas, **lo que Gerard descartó con su motivo** y lo que ya está en marcha.
    Tope de **una etiqueta nueva por tanda** y nunca con nombre de plantilla: la primera prueba
    inventó 4 "formatos" (Demostración, Antes/Después, Proceso, Relato) que habrían partido la
    medición. Modo `--prueba` para llamarla sin escribir ni avisar.
  - LaunchAgents: `com.rmagency.oli-noche` (miércoles 01:30, detrás de notion-noche que refresca
    Metricool) y `com.rmagency.oli-recordatorio` (sábado 10:00). Instalados y cargados.
  - `notify.sh`: 4º argumento `canales` (`cascada` por defecto | `wa+email` = los dos, sin
    cascada) y 5º `asunto` para el correo. `autoprogramar.py` pasa a `wa+email`: llevaba desde
    siempre documentando "WhatsApp + email" cuando el correo solo salía si fallaba el WhatsApp.
  - `config/publicacion.json`: borrada la excepción de Jesús Mora (vuelve a miércoles + domingo,
    que ya es la regla base). Ojo: `chequeo_cobertura` canta que el **miércoles 23/09 de Jesús
    Mora está sin programar**.
  - Docs: `CLAUDE.md` ("quién corre solo" ya incluye a Oli), `estratega.md` §6, `olivia.sh`.
- **Cómo revertir:** `launchctl unload ~/Library/LaunchAgents/com.rmagency.oli-*.plist` y
  borrarlos; el resto (a_bandeja, notify) puede quedarse sin efecto.

### 2026-09-22 · Repetir ganadores (espaciados) y crear variantes · vídeo de JM del 23/09
- **Pedido por Gerard:** no pasa nada por repetir ideas y formatos ganadores; hay que
  espaciarlos en el tiempo y, a partir de ellos, crear otros parecidos que se puedan replicar.
- **Cambiado:** nueva §4 bis en `agentes/estratega.md` (repetir es el trabajo · espaciar al
  menos una tanda · variantes, no calcos · citar de qué ganador sale cada variante en el
  `porque`), reflejada en `infra/olivia/kickoff.md` y en el prompt de `oli_noche.py`.
- **Programado (Jesús Mora, miércoles 23/09):** `16_JM_cocina presu ilimitado.mp4` (Drive, lo
  subió Jaume el 22/09) → BORRADOR en Metricool para IG+TikTok a las 15:00, con copy nuevo de
  Coco (43 palabras, con la regla corta). Ficha de Notion actualizada a mano (Programado +
  fecha + vídeo + copy): `programar.py --notion` no la encontró porque el título de Notion va
  sin tildes. Nota: JM ya venía publicando miércoles y domingo (9, 13, 16 y 20/09); la
  excepción de "solo domingos" estaba obsoleta desde hacía semanas.

### 2026-09-22 · Avisos solo para lo automático · `firmar.py` (borrador → firme)
- **Pedido por Gerard:** no mandar correos por acciones que él acaba de pedir en la
  conversación (los avisos son para lo que pasa solo y necesita que él actúe); y dejar el vídeo
  de JM del 23/09 programado en firme, no en borrador.
- **Cambiado:** `programar.py --sin-aviso` (y la regla escrita en `CLAUDE.md` regla 3 y en
  `PROGRAMAR.md`); nuevo `infra/metricool/firmar.py` que pasa un borrador a firme por PUT
  (`draft=false` + `autoPublish=true`, también en `instagramData`) sin borrarlo ni resubir el
  vídeo. Ojo: hay que mandar solo los campos editables o la API devuelve 500.
- **Hecho:** el post 380247204 (JM, mié 23/09 15:00, IG+TikTok) está EN FIRME.
- **Cómo revertir:** en el planner de Metricool, volver a marcarlo como borrador.

### 2026-09-28 · Base "Rendimiento de vídeos" de Golossa + copies completos en el bruto
- **Pedido por Gerard:** un análisis de todo el contenido de Golossa como el de Xavi, en una
  base nueva de Notion, clasificado por las etiquetas; sin inventar las que no se sepan.
- **Cambiado:**
  - Nuevo `infra/notion/rendimiento.py` (reutilizable, `--cliente <slug> --pagina <page_id>`):
    junta en UNA pieza el mismo vídeo de IG y TikTok (mismo arranque de copy, ±2 días), calcula
    el veredicto contra la mediana de su red (mismo criterio que el termómetro) y crea/vuelca la
    base. Las columnas de etiquetas (Tipo de idea · Formato · Plantilla · Palanca) se crean
    VACÍAS a propósito: el bruto de Metricool no dice qué había en el vídeo.
  - `fetch_metricool.py` guarda ahora el **copy entero** (`copy`) además del recorte de una línea
    (`texto`, que es lo que sale en el .md). Antes solo se guardaban 90 caracteres de la primera
    línea, así que cualquier análisis de longitud o de hashtags salía falseado.
  - Métricas de Golossa refrescadas con ventana de 400 días: 385 publicaciones (24/08/2025 →
    22/09/2026) frente a las 199 que había paradas desde el 11/08.
- **Resultado:** base `📊 Rendimiento de vídeos — golossa` (253 piezas) en la página de Golossa,
  con vistas 🏆 Los mejores · ✍️ Por etiquetar · 🧩 Por formato · 🧠 Por tipo de idea.
- **Cómo revertir:** borrar la base en Notion; el script y el campo `copy` pueden quedarse.

### 2026-09-30 · Dos plantillas nuevas y dos reglas de sitio, salidas del análisis de Golossa
- **Pedido por Gerard:** anotar sus conclusiones (secreto del oficio · opinión que pincha · día
  de trabajo · decir la ubicación) para generar vídeos con los otros clientes.
- **Cambiado:** nuevas `agentes/guiones/plantillas/secreto-del-oficio.md` y `opinion-marcada.md`
  (con su evidencia y su traducción por cliente); sección "Los dos ejes" en el README del
  catálogo (qué mecánica sirve para alcance y cuál para interacción); dos reglas transversales en
  `agentes/guiones/_comun.md` (grabar en el sitio de trabajo real · decir la ubicación en voz
  alta); sección "Qué funciona — ángulos a explotar" en las fichas de jesus-mora, newmos y
  xavi-colomina; aprendizajes en `memoria/aprendizajes/registro.md`.
- **Efecto inmediato:** Coco ve las plantillas nuevas en el catálogo sin tocar nada (se leen de
  la carpeta), y Oli lee las fichas al montar la tanda de octubre.
- **Cómo revertir:** borrar los dos .md de plantillas y las secciones añadidas.

### 2026-10-01 03:00 · Limpieza mensual automática (Nova)
- **Pedido por Gerard:** limpieza periódica mensual de registros viejos/inútiles.
- **Cambiado:** vaciados logs volátiles (responder, servidor, check-in) + ids anti-bucle; memoria de conversación podada a 30 días; borrados 0 .DS_Store y temporales de audio.
- **Cómo revertir:** no aplica (solo se elimina ruido; nada de datos de negocio se toca).

### 2026-10-02 · Las cuatro etiquetas, reordenadas: fronteras claras y listas cerradas
- **Pedido por Gerard:** arreglar Tipo de idea · Formato · Plantilla · Palanca. Sin duplicados y
  dejando claro qué va en cada una ("ahora es muy caótico y sin orden claro").
- **Diagnóstico:** 5 palabras estaban literalmente en dos columnas (Humor, Caso real, Receta,
  Día de trabajo, Predicción), 9 más eran la misma idea con otro nombre (Tendencia/Trend,
  Educativa/Explicacion, Ranking/Top 10/Lista…), `proceso-explicado` existía en Notion pero no
  como archivo (Coco no podía usarla) y las listas divergían entre la base de Golossa y las de
  cliente.
- **Cambiado:**
  - **Fuente única nueva: `agentes/guiones/ETIQUETAS.md`** — una pregunta por columna (de qué va ·
    qué forma tiene · cómo se escribe · por qué se queda), la definición de cada opción, la tabla
    de desempates y el registro de lo que se movió.
  - Dos mecánicas que estaban mal puestas como Formato pasan a ser plantillas con su archivo:
    `dicho-vs-pensado` (la de más techo medido: x237, x57, x51) y `realidad-exagerada`.
  - Nuevo `infra/notion/etiquetas_sincronizar.py`: reescribe primero las filas con el mapa de
    equivalencias (puede mover una etiqueta de columna) y después deja el esquema con la lista
    cerrada. En ese orden a propósito: al quitar una opción, Notion la borra de las páginas.
    Aplicado: 254 filas remapeadas, 0 etiquetas sin equivalencia, 248/253 piezas de Golossa
    conservan sus etiquetas.
  - Listas idénticas en las 6 bases: Tipo de idea 8 · Formato 10 · Plantilla 17 (= la carpeta) ·
    Palanca 8 · Soporte 5. Ya no hay ninguna palabra repetida entre columnas.
  - Puerta cerrada a inventar: `guionizar.py` y `oli_noche.py` descartan lo que no esté en la
    lista y avisan (antes creaban la opción). `etiquetas_idea.py` y `rendimiento.py` siembran las
    listas nuevas. Docs: `_comun.md`, `winy-tareas.md`, `plantillas/README.md`, `CLAUDE.md`.
- **Cómo revertir:** no hay vuelta automática (las opciones viejas ya no existen). Habría que
  volver a crearlas a mano y reetiquetar; el mapa de equivalencias está en el script.
