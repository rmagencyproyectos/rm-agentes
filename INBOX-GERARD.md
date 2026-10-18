# INBOX de Gerard — bandeja de Winston

> Winston vuelca aquí el digest de cada ciclo y los avisos. Se escribe SIEMPRE (es el
> último eslabón de la cascada de notificación). Lo más reciente arriba.

---

### 2026-07-26 · 🚀 Mejoras nuevas: recordatorios, ideas en Notion, links y calendario

Cuatro cosas nuevas. Dos ya funcionan solas; dos necesitan que actives algo tú (10 min, ver
`infra/SETUP.md` puntos 5 y 6).

**Ya funcionando** ✅
- **Recordatorios**: escríbeme "recuérdame ..." y lo apunto solo (gratis, sin gastar modelo). Si
  le pones fecha ("el jueves") o cliente, lo ordeno por vencimiento y marco ⚠️ lo que se pasa.
- **Calendario para reenviar**: dime "prepara el calendario de <cliente>" y te propongo el orden
  de los vídeos, tú lo ajustas, y te devuelvo la lista lista para reenviar (solo *día → título*,
  sin saludos). El copy te lo dejo en la carpeta del ciclo. En Metricool NO toco nada hasta tu OK.

**Necesitan que lo actives** 🔔
- **Ideas en Notion**: creé la base *"Bandeja de Ideas RM"*. Para que yo pueda escribir ahí (y
  guardar ideas desde links de IG/TikTok que me mandes), necesito una clave de integración de
  Notion → `SETUP.md` punto 5.
- **Leer los vídeos del Drive + programar en Metricool**: necesito una credencial de Google
  (service account) y un par de librerías → `SETUP.md` punto 6. Además MSM y Xavi aún no están en
  ese Drive: cuando estén, dime y añado sus carpetas.

Mientras no los actives, si intento usarlos te aviso en corto de que falta configurarlos (no se
rompe nada).

### 2026-07-26 · ✅ Calendario resuelto — vale tu WhatsApp del 25/07

Confirmaste que manda tu mensaje del 25/07. Ya está aplicado e **igual en los dos sitios**
(`config/calendario-publicacion.md` y `REGLAS` de `chequeo_cobertura.py`):

- **Newmos** → solo **domingo**.
- **Golossa, Jesús Mora, MSM, Xavi** → **miércoles + domingo**.
- **Midtown** → **martes, jueves y sábado** (martes, corta).

El chequeo de cobertura ya avisa con estas reglas. Aviso anterior (abajo) queda cerrado.

### 2026-07-26 · ⚠️ El calendario de publicación no cuadra — hace falta tu confirmación

Tu último WhatsApp del 25/07 se quedó **sin aplicar**: Winy murió con "session limit" justo al
contestarlo (era el fallo de coste, ya arreglado). Ahora mismo hay **tres versiones distintas**
de los días de publicación:

| Fuente | Qué dice |
|---|---|
| Tu mensaje del 25/07 (el más reciente) | Newmos **solo domingos** · resto **mié + dom** · Midtown **mar, jue y sáb** |
| `config/calendario-publicacion.md` | **Todos** mié + dom (sin excepción de Midtown) |
| `infra/metricool/chequeo_cobertura.py` (`REGLAS`) | resto mié + dom · Midtown jue + sáb + mar (corta) |

Mientras no cuadren, el **chequeo de cobertura avisa sobre huecos que quizá no existen** (o se
calla sobre alguno que sí). Dime cuál vale y lo dejo igual en los tres sitios.

### 2026-07-25 · Infra + canal WhatsApp operativos ✅
- Docker + Evolution API v2.3.7 levantados (`infra/`), contenedores con auto-reinicio.
- WhatsApp vinculado a tu número (34601238957) y **notificador probado**: camino feliz
  (WhatsApp+INBOX) y fallback (solo INBOX si Evolution cae). Script: `infra/notifier/notify.sh`.
- Arranque tras reinicio configurado (Docker start-on-login + auto-login). Energía: `sleep 0`.

**Pendiente (menor):** cablear el fallback de **email** real (hoy solo marca en INBOX) —
decidir vía: app-password SMTP de Gmail, o disparo por el conector MCP de Gmail desde Winston.

### 2026-07-25 · Sistema montado (Fase 0)
Hub `AGENTES RM/` creado. Listo:
- 5 SOP de agente (`agentes/`), con TBD marcados donde hacen falta tus decisiones.
- 2 capas de memoria: fichas de los 6 clientes v1 (`memoria/clientes/`) + registro de
  aprendizajes sembrado (`memoria/aprendizajes/`).
- 3 briefs de copy verbatim guardados: Jesús Mora, Golossa, Midtown.
- Bus de ciclo (`ciclos/`) con manifest piloto de Xavi.

**Pendiente de ti (ver §7 del plan):** decidir los TBD de los agentes (fuente de métricas
del Estratega, alcance del Editor, reglas de bloqueo del QA, briefs de Xavi/Newmos).

### 2026-07-25 22:24 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 MSM: mié 29/07 sin programar
🔴 Newmos: mié 29/07 sin programar
🟡 Golossa: dom 02/08 en borrador
🟡 Midtown: sáb 25/07 en borrador
✅ Jesús Mora: ok hasta mié 05/08

### 2026-07-28 17:18 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• Golossa: Prueba noche (para que Coco la genere de madrugada
  https://app.notion.com/p/3ab496ca6d5181d9af85c05dc397fc35

Toca el enlace para abrirla en Notion 📱

### 2026-07-29 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay un par de decisiones que tomar, y tres clientes sin programa.

*Para hoy* 🔔
• Xavi: estrategia de los 40 vídeos (orden de salida, cuál sacar primero, ritmo). Septiembre espera.
• MSM (hoy), Midtown (mañana), Newmos (domingo): qué programar en esos huecos.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — flujo nuevo en marcha (copy VR), borrador esperado hoy · cubierto hasta 09/08
• 🟡 Golossa — domingo en borrador (2 vídeos)
• ⏳ Xavi — 40 vídeos editados, estrategia pendiente

*Recordatorios*
• Tu nota de análisis mensuales: deadline 31/07, sin arrancar aún. Sin prisa pero que no se vaya de vista.

Cuando quieras me lo dices 🙌

### 2026-07-29 00:45 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 2 idea(s), listas para grabar:

• Golossa: Prueba noche 2 (test automático de las 00:45)
  https://app.notion.com/p/3ab496ca6d5181599fd0e8ad1c5df999
• MsM Models: idea
  https://app.notion.com/p/3ab496ca6d5181fe94cee43ce624cba0

Toca el enlace para abrirla en Notion 📱

### 2026-07-30 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Midtown: jue 30/07 sin programar
🔴 MSM: dom 02/08 sin programar · 🎬1
🔴 Newmos: dom 02/08 sin programar
🟡 Golossa: dom 02/08 en borrador · 🎬1
✅ Jesús Mora: ok hasta dom 09/08 · 🎬1

### 2026-07-30 00:45 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• Golossa: TEST Codex - idea borrador de acceso (puedes borra
  https://app.notion.com/p/3ac496ca6d5181b285bffb295c29cd36

Toca el enlace para abrirla en Notion 📱

### 2026-08-02 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Lo que toca decidir hoy es más bien cosa de esta semana — hay varios huecos sin cubrir y uno pendiente tuyo que pasó.

*Para hoy*
🔔 Xavi: necesita tu OK en la estrategia de publicación de los ~40 vídeos. Qué sale, en qué orden y cuándo (calendario). Edición ya está lista; si das OK hoy podemos arrancar a blindar la cobertura de septiembre.

*Cómo va lo pendiente*
• ✅ Jesús Mora — cubierto hasta mié 12/08, distribución en marcha
• 🔔 Xavi — edición adelantada, espera tu estrategia
• 🔴 Golossa — sin programar para mié 12/08
• 🔴 Midtown — sin programar para mar 04/08 (ojo, en dos días)
• 🔴 Newmos — sin programar para dom 09/08
• 🟡 MSM — mié 05/08 tiene copys pero falta IG o TikTok

*Recordatorios*
• ⚠️ Análisis mensuales: tenías para el 31/07, ¿todavía quieres que corra hoy?

Cuando salgas de la estrategia de Xavi avisas y vamos a tapar huecos 🙌

### 2026-08-03 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Midtown: mar 04/08 (corta) sin programar
🔴 Newmos: dom 09/08 sin programar
🟡 Golossa: mié 05/08 en borrador
🟡 MSM: mié 05/08 falta IG o TikTok
✅ Jesús Mora: ok hasta mié 12/08

### 2026-08-03 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Midtown toca mañana sin programar: eso es lo urgente. Y Xavi espera tu OK en la estrategia de publicación de los 40 vídeos.

*Para hoy* 🔔
• Xavi: review de estrategia (40 vídeos editados, falta calendario).
• Midtown: mar 04 sin nada. ¿Qué sale?

*Cómo va lo pendiente*
• ✅ Jesús Mora — cobertura tranquila hasta 12/08, copies en marcha, distribución en curso
• 🔔 Xavi — 40 ediciones adelantadas, espera tu OK
• ❌ Midtown — mar 04 sin programar (MAÑANA)
• ❌ Newmos — dom 09 sin programar
• ⏳ Golossa — mié 05 en borrador
• ⚠️ MSM — mié 05 falta asignar a IG o TikTok

*Recordatorios*
• Tu nota de análisis mensuales (del 31/07) sigue pendiente.

Todo lo demás tranquilo 🙌

### 2026-08-04 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Mañana toca grabar con Jesús Mora y Golossa — son tus deadlines antes de que se queden sin cobertura.

*Para hoy*
🔔 Xavi: tienes la estrategia de publicación lista (qué vídeos, orden, calendario de los 40 editados). Dale el OK cuando revises.

🔴 Midtown: hoy sin programar (cobertura martes corta). Para la próxima semana, que paran agosto.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — copies+distribución en curso (ciclo 2026-07).
• ⏳ Xavi — 40 vídeos editados listos, espera estrategia.
• 🔴 Midtown — sin programación hoy (retoman septiembre).
• 🔴 Newmos — dom 09/08 sin programar.
• 🟡 Golossa — mié 05/08 en borrador.
• 🟡 MSM — mié 05/08 falta IG o TikTok.

*Recordatorios*
• Análisis mensuales (vencida desde 31/07) — aún sin dejarse correr.

La estrategia de Xavi espera tu OK, los 40 están listos 👍

### 2026-08-05 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Las grabaciones se te cierran. Hoy hay 5 huecos sin programar, pero eso es lo de menos.

*Para hoy* 🔔
• *Jesús Mora*: HOY sin programación + tienes que grabar esta semana (ok hasta 12/08). Urge.
• *Golossa*: hoy en borrador + grabar antes de que se agote. Primero: confirma cobertura hasta cuándo.
• *Xavi*: 40 vídeos listos. Calendario de publicación espera tu OK.
• *Midtown*: martes 11/08 corta sin programar.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — copies en curso, distribución en marcha. Flujo probado (copy → vídeo → Metricool).
• ⏳ Golossa — borrador 05/08, cobertura sin confirmar.
• ❌ Midtown — mar 11/08 sin programar.
• ❌ MSM — mié 12/08 sin programar.
• ❌ Newmos — dom 09/08 sin programar.

*Recordatorios*
• Análisis mensuales (nota 31/07): retrasada. Dime si quieres que proceda.
• Grabaciones Jesús Mora + Golossa: esta semana es el momento.

Cuando decidas, vamos a por las grabaciones. 🙌

### 2026-08-06 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 5 a revisar:

🔴 Midtown: mar 11/08 (corta) sin programar
🔴 Jesús Mora: mié 12/08 sin programar
🔴 MSM: dom 16/08 sin programar
🟡 Golossa: mié 12/08 en borrador
🟡 Newmos: dom 09/08 falta IG o TikTok

### 2026-08-07 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi espera tu OK, pero tienes dos rodajes vencidos que no pueden esperar.

*Para hoy*

🔔 Xavi: *estrategia de publicación*. Tiene ~40 vídeos editados y listos. Falta que decidas qué, orden y cuándo (toca en septiembre, pero necesito tu OK para que Olivia lo defina).

⚠️ Rodajes vencidos — tiran contenido si no rodas esta semana:
• Jesús Mora: grabar antes del 12/08 (fin de cobertura)
• Golossa: confirmar hasta cuándo está cubierto y grabar antes

🔴 Huecos sin programar (próximos 10 días):
• Midtown 11/08 — sin nada (4 días)
• Jesús Mora 12/08 — sin nada (5 días)
• Golossa 12/08 — en borrador
• Newmos 09/08 — falta IG o TikTok (2 días)
• MSM 16/08 — sin programar

*Cómo va lo pendiente*

⚠️ Jesús Mora — ciclo activo (copies y distribución OK). Prueba de flujo de programación funcionó. Urgencia: grabar.

⚠️ Golossa — sin ciclo activo. Cobertura ajustada. Urgencia: grabar.

⏳ Midtown — pausa en agosto (reunión 28/08). Necesita cobertura el 11/08.

⏳ Xavi — 40 vídeos listos, edición adelantada. Espera estrategia.

✅ Newmos — casi cubierto (falta red del 09/08).

✅ MSM — sin urgencias hasta el 16/08.

*Recordatorios*

• Análisis mensuales: nota vencida desde 31/07. ¿Sigue en pie?
• Las dos notas de grabación llevan 2 días. Confirma los rodajes ASAP.

Dale, cuando quieras seguimos 🙌

### 2026-08-08 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Poca cosa hoy, pero hay dos frentes urgentes: Xavi espera tu estrategia (40 vídeos listos) y dos clientes que grabar.

*Para hoy* 🔔
🔔 Xavi: 40 vídeos editados, listos. Necesito que definas la estrategia (qué sacar, orden, cuándo).
⚠️ Grabaciones urgentes: Jesús Mora y Golossa. Hoy o mañana máximo (cobertura agotada 12/08).

*Cómo va lo pendiente*
• ✅ Xavi — edición adelantada, estrategia espera tu OK
• ⏳ Jesús Mora — copies+distribución en curso
• ⏳ Golossa — cobertura en borrador (12/08)
• ⏳ Midtown — martes 11/08 sin programar (corta), reunión 28/08
• ⏳ MSM — domingo 16/08 sin programar
• ⏳ Newmos — domingo falta IG o TikTok

*Recordatorios*
⚠️ Análisis mensuales: quedó correr de noche (nota 31/07).

Avisa cuando hayas decidido 🤙

### 2026-08-09 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tienes la estrategia de Xavi pendiente, cinco huecos sin programar y dos notas que vencieron hace días.

*Para hoy*

🔔 Xavi: necesitas dar luz verde a la estrategia de publicación (qué vídeos, orden, calendario). Tiene ~40 listos para septiembre.

🔴 Cinco huecos sin programar:
• Midtown: martes 11/08
• Jesús Mora: miércoles 12/08
• Golossa: miércoles 12/08 (en borrador, espera tu OK)
• MSM: domingo 16/08
• Newmos: hoy falta IG o TikTok

*Cómo va lo pendiente*

• ✅ Xavi — 40 vídeos editados y listos, adelantado
• ⏳ Jesús Mora — copies en curso, distribución en curso
• 🟡 Golossa — programación en borrador
• 🔴 Midtown — sin cobertura (paran agosto, vuelven en sept)
• 🔴 MSM — sin cobertura a partir del 16
• ⏳ Newmos — hoy incompleto (falta IG o TikTok)

*Recordatorios*

⚠️ Tres notas tuyas vencidas:
• Análisis mensuales (31/07)
• Grabar con Jesús Mora (05/08)
• Grabar con Golossa (05/08)

Reunión con Midtown: 28/08.

Cuando quieras me dices y seguimos 🙌

### 2026-08-10 00:30 · COBERTURA · normal (enviado por: email)
📅 *Cobertura* — 5 a revisar:

🔴 Midtown: mar 11/08 (corta) sin programar
🔴 Jesús Mora: mié 12/08 sin programar
🔴 MSM: dom 16/08 sin programar
🔴 Newmos: dom 16/08 sin programar
🟡 Golossa: mié 12/08 en borrador

### 2026-08-13 00:30 · COBERTURA · normal (enviado por: email)
📅 *Cobertura* — 2 a revisar:

🔴 Golossa: mié 19/08 sin programar
🔴 MSM: dom 16/08 sin programar
⏸ Midtown: en pausa hasta 31/08
✅ Jesús Mora: ok hasta dom 23/08
⏸ Newmos: en pausa (sin fecha de vuelta)
⏸ Xavi: en pausa hasta 31/08

### 2026-08-13 00:47 · GUIONES · normal (enviado por: email)
✍️ Coco guionó anoche 8 idea(s), listas para grabar:

• Golossa: Obrador · El encargo, de principio a fin
  https://app.notion.com/p/3ba496ca6d5181a19cc3c5c69aed36f9
• Golossa: Obrador · De masa a cookie
  https://app.notion.com/p/3ba496ca6d5181b6993ac433828de13b
• Golossa: Obrador · Cheesecake o cookie: Jonathan tiene que 
  https://app.notion.com/p/3ba496ca6d51811aa4d6ee8b515e1b2c
• Golossa: Obrador · Las 6 de la mañana
  https://app.notion.com/p/3ba496ca6d5181f69dc5eb6da179231e
• Golossa: Obrador · Cómo sabemos que está lista
  https://app.notion.com/p/3ba496ca6d5181e99470d67c902a68f6
• Golossa: Obrador · Lo que entra en una tanda
  https://app.notion.com/p/3ba496ca6d518113b89bf4c9adf0e4ae
• Golossa: Obrador · El error que arruina una cheesecake
  https://app.notion.com/p/3ba496ca6d51812f89a3ce0339a86e40
• Golossa: Obrador · Por qué la hacemos así
  https://app.notion.com/p/3ba496ca6d5181dfaa3df8da892a3bd4

Toca el enlace para abrirla en Notion 📱

### 2026-08-14 00:46 · GUIONES · normal (enviado por: email)
✍️ Coco guionó anoche 3 idea(s), listas para grabar:

• Golossa: Carrusel fotos + historia cliente no ha pagao y ha
  https://app.notion.com/p/3bb496ca6d51817bb6cbf7b9a3d1f96f
• Golossa: Grabando producto “mas cerca, mas cerca” hasta peg
  https://app.notion.com/p/3bb496ca6d5181c1b197fd12462be16a
• Golossa: Video estatico cookies haciendose + marcha alante 
  https://app.notion.com/p/3bb496ca6d5181ce9b91c418c2d0cc98

Toca el enlace para abrirla en Notion 📱



- ⚠️ 2026-08-14 14:26 · guionizar: [golossa] Obrador · Cómo sabemos que está lista no se pudo guionizar: claude salió 1: 

- ⚠️ 2026-08-14 14:28 · guionizar: [golossa] Obrador · Cómo sabemos que está lista no se pudo guionizar: claude salió 1: 

### 2026-08-15 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay dos huecos de cobertura esta semana y una OK de Xavi pendiente.

*Para hoy*
🔔 Xavi: la estrategia espera tu visto — 56 piezas cortas, podcast sin montar, publicación desde sept a 3-4/semana.
🔴 Golossa: mié 19/08 sin programar, tiempo justo.
🔴 MSM: dom 16/08 sin programar.
📋 Análisis julio: faltan 5 (MidTown, Golossa, Newmos, MSM, Jesús Mora). Brutos de Metricool listos. ¿Arranco el Analista?

*Cómo va lo pendiente*
• ✅ Jesús Mora — copies en curso, distribución activa, ok hasta 23/08.
• 🔔 Xavi — edición adelantada; espera tu OK en estrategia.
• ⚠️ Golossa — edición + programación; mié 19 sin cubrir.
• ⚠️ MSM — dom 16 sin cubrir.
• ⏸ Midtown — pausa hasta 31/08.
• ⏸ Newmos — pausa.

*Recordatorios*
• Dos notas tuyas sin resolver: grabar con Jesús Mora y Golossa (vencidas 2026-08-05).
• Bandeja atascada: 17 ideas sin triar (11 con +7 días). 8 con cliente → solo esperan tu Aprobada en Notion para guionizar.
• Reunión Midtown: 28/08.

Avísame cuándo atacamos 🙌

### 2026-08-16 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres cosas que no pueden esperar.

*Para hoy*
🔔 Xavi — estrategia lista. Dale OK.
🔔 Bandeja — 17 ideas sin triar (11 viejas). Las 8 con cliente se guionizarían esa noche si das luz.
⚠️ Jesús Mora — vencido. Necesita grabación.
⚠️ Golossa — vencido. Confirma cobertura.

*Cómo va lo pendiente*
• ⚠️ Golossa — edición pendiente, mié 19 sin programar
• ⚠️ MSM — pausa, mié 19 sin cobertura
• ✅ Jesús Mora — ok hasta dom 23/08
• ⏸ Midtown — pausa hasta 31/08
• ⏸ Newmos — pausa (sin retorno)
• 🔔 Xavi — adelantado, en espera de tu OK

*Recordatorios*
• Análisis de julio sin hacer: Golossa, MSM, Midtown, Newmos, Jesús Mora
• Tus notas vencidas: arrancá análisis (31/07), grabar con Mora y Golossa (05/08)
• Con Jesús Mora: grabación un solo día en el taller
• Reunión Midtown: 28/08

Cuándo quieras movemos 🙌

### 2026-08-17 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Golossa: mié 19/08 sin programar · 🎬11
🔴 MSM: mié 19/08 sin programar
⏸ Midtown: en pausa hasta 31/08
✅ Jesús Mora: ok hasta dom 23/08
⏸ Newmos: en pausa (sin fecha de vuelta)
⏸ Xavi: en pausa hasta 31/08

### 2026-08-17 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Mié 19 te pilla a Golossa y MSM sin programación. Análisis de julio también esperando — faltan 5.

*Para hoy* 🔔
• Golossa y MSM: mié 19 sin programación (¿reprogramamos o nos lo saltamos?)
• Análisis mensuales: 5 de julio. ¿Sesión con el Analista?

*Cómo va lo pendiente*
• ⏳ Jesús Mora — distribución ok, cobertura hasta el 23
• ⏳ Xavi — edición ok, espera tu OK en fechas (septiembre)
• ⚠️ Golossa — sin programación para el 19, grabación atrasada
• ⚠️ MSM — sin programación para el 19
• ⏸ Midtown, Newmos — pausadas

*Recordatorios*
• Grabaciones (Jesús Mora, Golossa): llevan semanas. Todavía hay margen.
• Bandeja: 17 ideas sin triar. 8 con cliente listos para Aprobada → guionizarse esa noche.
• Reunión Midtown: 28/08.

### 2026-08-18 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tenemos cobertura que tapar y notas caducadas.

*Para hoy* 🔔

• 🔴 Golossa: mié 19/08 *sin programar* (11 piezas esperando en edición). Necesitas cobertura urgente.

• 🔴 MSM: mié 19/08 también vacío.

• Xavi: estrategia lista, falta concretar los días de publicación desde sept (3-4 piezas/semana). ¿Cuáles son?

• 5 análisis de julio sin cerrar (Midtown, Golossa, Newmos, MSM, Jesús Mora). Los brutos de Metricool deberían estar en correo.

*Cómo va lo pendiente*

• ✅ Jesús Mora — copys en curso, cobertura ok hasta dom 30/08
• ⏳ Golossa — edición adelantada, esperando programación
• ⏳ Xavi — estrategia listo, edición adelantada, espera tu OK
• ⏸ Midtown — pausa hasta 31/08 (reunión 28/08)
• ⏸ Newmos — pausa
• ⏸ MSM — pausa

*Recordatorios*

⚠️ Dos notas del 05/08 sin cerrar (ambas ⚡alta):
  • Grabar con Jesús Mora: cobertura ok hasta 30/08, probablemente ya hecho
  • Grabar con Golossa: confirmar hasta cuándo están cubiertos

• Bandeja: 17 ideas sin triar (11 llevan >7 días)
• Proyecto nuevo para análisis mensuales (nota del 31/07)

Mándame cuando arranques y seguimos 🔥

### 2026-08-19 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tienes dos piezas sin programar hoy y una estrategia de Xavi que solo espera tu OK. Luego está lo de las grabaciones.

*Para hoy* 🔔
• Xavi: estrategia lista (56 piezas, publicación desde sept a 3-4/semana). Dale luz verde cuando quieras.
• Golossa: *mié 19/08 sin programar*. Toca edición y programación esta semana. ¿Hay videos listos para pasar a Metricool?
• MSM: *mié 19/08 sin programar* también.
• Análisis de julio: te llegan los brutos de 5 clientes en el correo. Arrancas sesión del Analista cuando estés.

*Recordatorios urgentes* ⚠️
• Grabación Jesús Mora: vencida hace 2 semanas (ok hasta 30/08, espacio justo). Concretar cuándo.
• Grabación Golossa: tenías apuntado hace 14 días que ya. ¿Hasta cuándo tienen cobertura?
• Bandeja: 17 ideas paradas (16 llevan >7 días). Hay 8 listas para guionizar apenas apruebes.

*Cómo va lo demás*
• Jesús Mora: distribución en curso, primer flujo validado ✅
• Midtown y Newmos: en pausa (reunión Midtown: 28/08)

Si necesitas que repita algo o tienes las respuestas, me lo dices.

### 2026-08-20 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Golossa: mié 26/08 sin programar · 🎬7
🔴 Midtown: mar 01/09 (corta) sin programar
🔴 MSM: dom 23/08 sin programar
🟡 Xavi: mar 01/09 en borrador
✅ Jesús Mora: ok hasta dom 30/08
⏸ Newmos: en pausa (sin fecha de vuelta)

### 2026-08-20 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Toca mover varias fichas hoy.

*Para hoy* 🔔

• 🔔 Xavi (ciclo anterior): necesito tu OK en la estrategia. De las 56 piezas del inventario real, ¿cuáles le doy luz verde a Programación para septiembre (3/semana desde el 01/09)?

• ❌ Xavi (septiembre): *presentación aún SIN montar* y sale el martes 01/09. Material grabado, storyboard en Notion. ¿Cuándo se la encargo al Editor?

• 🔔 Bandeja de ideas: 17 pendientes de triar (16 llevan +7 días). 8 ya tienen cliente y solo esperan tu OK para que Coco las guionize esa noche. ¿Aprobadas?

• 🔔 Análisis de julio: 5 clientes listos (Midtown, Golossa, Newmos, MSM, Jesús Mora). Los brutos de Metricool ya están en tu correo → ¿arranco sesión?

*Cómo va lo pendiente*

• ⏳ Jesús Mora — distribución en curso, copies en curso. Programación ok hasta el 30/08.

• ⏳ Xavi — 2026-07 en edición adelantada, espera OK. 2026-09 arranque el 01/09, sin la presentación montada.

• 🔴 Golossa — edición + programación en curso (toca a Editor). Hueco sin programar el 26/08.

• 🔴 Midtown — parada en agosto. Sin programación el 01/09.

• 🔴 MSM — sin programación el 23/08.

• ⏸ Newmos — en pausa.

*Recordatorios*

• ❌ Grabar con Jesús Mora: nota del 05/08, aún pendiente. Tocaba hace 2 semanas.

• ❌ Grabar con Golossa: nota del 05/08, aún pendiente. Falta confirmar hasta cuándo tienen cubierto.

• Reunión Midtown: miércoles 28/08.

Cuando me digas de Xavi y la Bandeja, seguimos 🙌

### 2026-08-20 00:49 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 5 idea(s), listas para grabar:

• Xavi Colomina: Empuñadura NO continental
  https://app.notion.com/p/3b2496ca6d518073906df95da94aa5ae
• Xavi Colomina: Sentido comun en el padel
  https://app.notion.com/p/3b2496ca6d51807c9462ff4434269f1a
• Xavi Colomina: Reves a 2 manos
  https://app.notion.com/p/3b2496ca6d5180d38336c9a96af00c10
• Xavi Colomina: Basculas mal en el fondo
  https://app.notion.com/p/3b2496ca6d5180c190c3c9f023682977
• Xavi Colomina: Mala posicion de ataque
  https://app.notion.com/p/3b2496ca6d518055ad3edc65406f4653

Toca el enlace para abrirla en Notion 📱

### 2026-08-21 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Acumulamos un poco: 3 clientes sin programar, la presentación de Xavi sin montar, y 15 ideas en la bandeja esperando triaje.

*Para hoy*
🔔 Xavi — la presentación del 01/09 no está montada aún. Material grabado (13/08) y storyboard en Notion, solo falta que Editor la monte. Necesita tu OK para arrancar.

⚠️ Huecos sin programar — casi encima:
• MSM: domingo 23/08
• Golossa: miércoles 26/08
• Midtown: martes 01/09

🔔 Bandeja — 15 ideas esperan triaje, 7 ya tienen cliente y solo necesitan tu OK en Estado=Aprobada para guionizarse esa noche.

*Cómo va lo pendiente*
✅ Xavi (2026-07) — espera OK en estrategia. Inventario: 56 cortas + podcast + ~2h clases. Publicación desde sept a 3-4/semana, 4 meses de colchón.

⏳ Xavi (2026-09) — copies listos, 52 piezas en Notion hasta 29/12, 12 borradores en Metricool. Presentación 01/09 espera OK en edición.

✅ Jesús Mora — cubierto hasta domingo 30/08. Copies en curso, distribución en curso.

⏳ Golossa — semana 3: edición y programación. 3 huecos en cobertura.

⏸ Midtown — pausa agosto, retoman septiembre. 01/09 sin programar.

⏸ MSM — 23/08 sin programar.

⏸ Newmos — en pausa.

*Recordatorios*
⚠️ Notas vencidas:
• Análisis mensuales (31/07) — no corrieron. Falta proyecto nuevo.
• Grabar Jesús Mora (05/08) — programación ok hasta 12/08, hoy es 21/08.
• Grabar Golossa (05/08) — necesitas confirmar hasta cuándo tienen cubierto.

📅 Reunión Midtown — 28/08 (próxima semana)

Cuando tengas un rato me dices qué hacer con los huecos de programación y si Editor arranca ya con la presentación, y seguimos 🙌

- ⚠️ 2026-08-21 00:47 · guionizar: [golossa] Comiendo despues de publicar reel viral no se pudo guionizar: no encontré JSON en la respuesta

### 2026-08-21 00:49 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 4 idea(s), listas para grabar:

• Golossa:  Obrador · Solo sonido INVENTADO
  https://app.notion.com/p/3c2496ca6d5181d5be29f49ca477c9fb
• Golossa: Estas trabajando y empieza a sonar tu cancion fav
  https://app.notion.com/p/3c2496ca6d51811780b9e7f06413e547
• Golossa: POV: el cliente que viene siempre a desayunar
  https://app.notion.com/p/3c2496ca6d5181638e99e4f8423d6719
• Golossa: Trabajador atiende de mas cerca a cliente
  https://app.notion.com/p/3c2496ca6d5181a9af5ccf4033db35e9

Toca el enlace para abrirla en Notion 📱

### 2026-08-22 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Programación rota en cuatro clientes y Xavi tiene dos piezas que no pueden fallar.

*Para hoy* 🔔
• Xavi — presentaciones 01/09 y 03/09 salen solas (autopublicar ON). ¿El Editor te confirma?
• Programación: sin cobertura en Golossa (mié 26), MSM (dom 23), Midtown y Xavi (mar 01). Toca despachar hoy.
• Bandeja — 19 ideas sin triar. 8 ya con cliente: un Estado=Aprobada y salen guionizadas esa noche.

*Cómo va lo pendiente*
• ⏳ Golossa — análisis sin arrancar
• ✅ Jesús Mora — ok hasta dom 30
• ⏳ Midtown — hueco mar 01 + reunión 28/08
• ⏳ MSM — dom 23 sin nada
• ⏳ Xavi — inventario listo, borrador mar 01 pendiente, estrategia ciclo 07 espera OK
• ⏸ Newmos — pausa

*Recordatorios*
• Grabar con Jesús Mora y Golossa (notas pasadas, confirmar hoy)
• Análisis de julio desde hace un mes

¿Por dónde? 🙌

### 2026-08-22 00:46 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• Golossa: Comiendo despues de publicar reel viral
  https://app.notion.com/p/3c2496ca6d51817bb9ebf068149c3e45

Toca el enlace para abrirla en Notion 📱

### 2026-08-23 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Poco que decidir hoy — Xavi (dos presentaciones críticas) y bandeja (8 ideas). Para el análisis de Golossa necesitas confirmar cobertura.

*Para hoy*
• 🔔 Xavi: dos presentaciones (01/09 y 03/09) sin montar. Con autopublicar activado, esos días quedan vacíos si no llegan. Chequea que estén en ruta.
• 🔔 Bandeja: 8 ideas con cliente listos, solo esperan tu OK.
• ⚠️ Golossa: confirma hasta cuándo tienen contenido cubierto (lo necesito para el análisis).

*Cómo va lo pendiente*
• ✅ Jesús Mora — ciclo 2026-07 en distribución, ok hasta 30/08.
• ⏳ Xavi — septiembre en programación (3/semana a 15:00), 12 posts listos y salen solos.
• ⚠️ Golossa — mié 26 sin programar + análisis del mes (esta semana).
• ⚠️ Midtown — mar 01/09 sin programar + reunión jueves 28/08.
• ⏳ MSM — hoy sin programar.
• ⏸ Newmos — en pausa.

*Recordatorios*
• 19 ideas en bandeja sin triar (15 > 7 días).

Avísame de Xavi y Golossa cuando puedas 🙌

### 2026-08-24 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Golossa: mié 26/08 sin programar · 🎬12
🔴 Midtown: mar 01/09 (corta) sin programar
🔴 MSM: mié 26/08 sin programar
🟡 Xavi: mar 01/09 en borrador · 🎬5
✅ Jesús Mora: ok hasta dom 30/08
⏸ Newmos: en pausa (sin fecha de vuelta)

### 2026-08-24 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hoy toca cuadrar tres frentes o cerramos agosto con clientes en blanco.

*Para hoy* 🔔
• *Xavi:* dos presentaciones para 01/09 y 03/09 sin montar, pero AUTOPUBLICAR está activo — si no llegan, esos días quedan vacíos (los posts salen igual, solo que sin vídeo). ¿Las hacemos o reprogramamos?
• *Golossa y Jesús Mora:* necesitan grabación confirmada hoy. Golossa: sin confirmar desde el 05/08. Jesús Mora: ok hasta 30/08, para grabar 1 semana antes era hace días. Arrancamos sesiones YA.
• *Xavi mar 01/09:* el borrador sigue ahí. Con autopublicar, toca que llegue limpio antes de la medianoche del 31/08.

*Cómo va lo pendiente*
• 🔴 Golossa — mié 26/08 sin programar, análisis mensual sin hacer
• 🔴 Midtown — mar 01/09 sin programar, reunión el 28/08 por vuelta a septiembre
• 🔴 MSM — mié 26/08 sin programar
• 🟡 Xavi (sept) — 12+1 posts EN FIRME desde 01/09 con autopublicar, dos presentaciones sin montar
• ✅ Jesús Mora — cobertura ok hasta 30/08
• ⏸ Newmos — pausa

*Recordatorios*
• Esas notas de 05/08 (grabar Golossa y Jesús Mora) ya son críticas hoy. Golossa sin confirmar, Jesús Mora con 6 días de cobertura.
• Bandeja: 20 ideas atascadas (15 con +7 días). 9 ya tienen cliente, solo esperan tu OK — esa madrugada salen guionizadas.
• Análisis de julio (nota del 31/07): sin arrancar.

Esperamos tu OK en las presentaciones de Xavi y el plan de grabaciones. De ahí se mueve todo. 🙌

### 2026-08-25 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Las dos presentaciones de Xavi que estrenan 01 y 03/09 siguen sin montar con autopublicar activado: esos días se quedan vacíos si no llegan.

*Para hoy* 🔔
• Xavi: montar presentaciones (01 y 03/09).
• Cobertura: rota en 4 — MSM 26/08, Golossa 30/08, Midtown 01/09, Xavi 01/09.
• Bandeja: 10 ideas con cliente esperan tu OK para guionizarse.

*Cómo va lo pendiente*
• ⚠️ Golossa — análisis del mes pendiente, sin cobertura 30/08
• ⚠️ Jesús Mora — distribución en curso, nota de grabar vencida (05/08)
• ⚠️ Xavi — septiembre casi listo (51 piezas), solo faltan esas dos presentaciones
• 🔔 Midtown — reunión mañana 28/08, retoman septiembre, sin cobertura 01/09
• ⚠️ MSM — sin cobertura 26/08
• ⏸ Newmos — en pausa

*Recordatorios*
• Notas de grabar vencidas: Jesús Mora y Golossa (ambas 05/08).
• Análisis de julio sin correr (31/07).

Con Xavi es hoy o mañana — después se complica.

### 2026-08-26 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres cosas requieren tu OK hoy.

*Para hoy* 🔔
• MSM: mié 26/08 sin programar. Es hoy.
• Xavi (01/09): borrador listo en Metricool. Va autopublicación a las 15h (IG + TikTok + YouTube), así que revisa los dos vídeos sin montar (01/09 y 03/09) antes de dar OK 🎬
• Bandeja: 9 ideas con cliente, solo les falta tu OK. Apruébalas y se guionizarán solos esta noche.

*Cómo va lo pendiente*
• ⏳ Golossa — mié 02/09 sin programar + analizar métricas del mes
• ⏳ Jesús Mora — distribución ok, pendiente guionizar ideas y cerrar grabación
• ❌ Midtown — mar 01/09 sin programar + reunión mañana (28/08)
• ⏸ Newmos — pausa sin fecha de vuelta

*Recordatorios*
• Grabar Jesús Mora y Golossa: notas sin hacer (confirma cuándo tienen cubierto)
• Análisis mensuales: pendiente desde 31/07
• Midtown mañana 28/08: reunión pactada

Qué haces con MSM y si das OK a Xavi — el resto se mueve solo 🚀

- ⚠️ 2026-08-26 00:45 · guionizar: [golossa] Referencia de Reel de Instagram guardada por Gerard (sin des no se pudo guionizar: no encontré JSON en la respuesta

### 2026-08-26 00:46 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• Golossa: Escojan ustedes, me dedico a vender cheesecakes o 
  https://app.notion.com/p/3c7496ca6d518187a0c6f52688e8c6ba

Toca el enlace para abrirla en Notion 📱

- ⚠️ 2026-08-26 01:40 · guionizar: [golossa] Referencia de Reel de Instagram guardada por Gerard (sin des no se pudo guionizar: no encontré JSON en la respuesta

- ⚠️ 2026-08-26 01:57 · guionizar: [golossa] Te perdono, pero no gratis  no se pudo guionizar: no encontré JSON en la respuesta

- ⚠️ 2026-08-26 01:57 · guionizar: [golossa] Referencia de Reel de Instagram guardada por Gerard (sin des no se pudo guionizar: no encontré JSON en la respuesta

- ⚠️ 2026-08-26 01:59 · guionizar: [rm-agency] Referencia de Reel de Instagram guardada por Gerard (sin des no se pudo guionizar: no encontré JSON en la respuesta

### 2026-08-27 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Golossa: mié 02/09 sin programar · 🎬18
🔴 Midtown: mar 01/09 (corta) sin programar · 🎬1
🔴 MSM: dom 30/08 sin programar
🟡 Xavi: mar 01/09 en borrador · 🎬5
✅ Jesús Mora: ok hasta dom 06/09 · 🎬13
⏸ Newmos: en pausa (sin fecha de vuelta)

### 2026-08-27 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay cuatro huecos sin cobertura y dos presentaciones de Xavi sin montar (y no esperan).

*Para hoy* 🔔
• Xavi: estrategia lista — ¿te va bien? Necesito tu OK para seguir.
• Bandeja: 9 ideas ya con cliente — apruébalas para que Coco las guionice esta noche
• Mañana (28/08): reunión con Midtown

*Cómo va lo pendiente*
• ⏳ Golossa — análisis de métricas y aprendizajes del mes · hueco: mié 02/09
• ⏳ Jesús Mora — guiones en marcha, preparando tomas y logística · cubierto hasta dom 06/09
• ⏳ Xavi — edición en curso, pero ojo: dos presentaciones (01/09 y 03/09) sin montar + autopublicar activado, si no llegan se saltan
• ⏳ Midtown — sin cobertura (mar 01/09) · mañana en la reunión te actualiza
• ⏳ MSM — hueco: dom 30/08
• ⏸ Newmos — en pausa

*Recordatorios*
• Xavi: 01/09 y 03/09 son críticas — edición sin hacer, autopublicar sin margen, plazos fijos
• Notas viejas (05/08): grabar con Jesús Mora y confirmar cobertura Golossa — ¿aún en pie?

Cuando quieras me dices y seguimos 🙌

### 2026-08-28 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Atasco en bandeja y cuatro huecos sin programar. Lo accionable está claro.

*Para hoy* 🔔

*Bandeja*: 17 ideas sin clasificar (14 llevan +7 días). 9 ya tienen cliente y esperan tu OK en "Aprobada" para guionizarse esa noche. Sin eso, nada arranca.

*Huecos sin programar*:
• mar 01/09 (Xavi, 5 piezas) — 🔥 crítico, autopublicar activado
• mié 02/09 (Golossa, 18 piezas)
• mar 01/09 (Midtown, 1 pieza)
• dom 30/08 (MSM)

*Xavi + crítico*: dos presentaciones sin montar (01/09 y 03/09) — fechas claves.

*Cómo va lo pendiente*

⏳ Golossa — espera análisis de agosto + aprendizajes. Hueco 02/09. Nota: grabar (vencida).
✅ Jesús Mora — cobertura OK (hasta 06/09). Copies y distrib en curso. Nota: grabar (vencida).
⏳ Midtown — reunión hoy (retoman sept). Hueco 01/09.
⏸ Newmos — pausa, sin fecha de vuelta.
🔥 Xavi — autopublicar ON: 12 posts salen solos a las 15:00 sin revisión. Hueco 01/09 (5 piezas en borrador). Crítico: dos presentaciones sin montar (01/09, 03/09). Espera tu OK en estrategia.

*Recordatorios*

⚠️ Notas vencidas (todas te tocan):
• Análisis julio (31/07) — lo necesita Golossa
• Grabar Jesús Mora (05/08) — urgente para guiones
• Grabar Golossa (05/08) — urgente para cobertura

Cuando quieras me dices y seguimos 🙌

### 2026-08-29 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
A 3 días del 01/09 hay puntos críticos.

*Para hoy* 🔔

• Xavi: dos presentaciones (01/09 y 03/09) sin montar + autopublicar activado. Si fallan, esos días quedan vacíos. 01/09 en borrador (5 piezas), 03/09 sin nada.
• Cobertura sin programar en 72 horas: Golossa 02/09 (18 piezas), Midtown 01/09 (1 pieza), MSM 02/09.
• Bandeja sin mover: 17 ideas sin triar, 9 con cliente esperan tu OK.

*Cómo va lo pendiente*

• ⏳ Xavi — 51 piezas listas, autopublicar activado, 100% pendiente de esas presentaciones
• ✅ Jesús Mora — cubierto hasta 06/09, copies en curso
• ⚠️ Golossa — espera análisis de julio
• ⚠️ Midtown — reunión tocaba ayer
• ⏸ Newmos, MSM — en pausa

*Recordatorios*

• Análisis mensuales de julio (vencido 31/07).
• Grabar con Jesús Mora y Golossa (vencido 05/08).
• Bandeja: 14 ideas llevan >7 días.

El finde es para Xavi.

### 2026-08-30 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Mañana arranca la autopublicación de Xavi (15:00 salen los posts solos) y hay un par de cosas que cerrar en septiembre.

*Para hoy* 🔔
• Golossa: análisis de agosto (métricas, aprendizajes, ideas del siguiente mes)
• Xavi: dos presentaciones sin montar (01/09 y 03/09) — si no llegan a tiempo esos dos días quedan vacíos
• Cobertura de septiembre: Golossa (02/09), Midtown (01/09), MSM (02/09) sin nada. ¿Dejan huecos o metemos algo?
• Bandeja: 17 ideas en cola, 15 con 7+ días. 9 ya tienen cliente — solo necesitan tu OK.

*Cómo va lo pendiente*
• ✅ Jesús Mora — ok hasta 06/09
• 🟡 Xavi — listo para mañana (ojo a las dos presentaciones)
• ❌ Golossa — análisis + 02/09 sin cobertura
• ❌ Midtown — 01/09 sin cobertura
• ❌ MSM — 02/09 sin cobertura
• ⏸ Newmos — en pausa

*Recordatorios*
⚠️ Notas sin cerrar:
• Análisis mensuales en proyecto nuevo (31/07)
• Grabar Jesús Mora (antes del 12/08)
• Confirmar cobertura Golossa
• Reunión Midtown (28/08 ya fue)

Cuando quieras me dices y seguimos 🙌

### 2026-08-31 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Golossa: mié 02/09 sin programar · 🎬16
🔴 Midtown: mar 01/09 (corta) sin programar · 🎬1
🔴 MSM: mié 02/09 sin programar
🟡 Xavi: dom 06/09 en borrador · 🎬5 ✍️1
✅ Jesús Mora: ok hasta dom 06/09 · 🎬13
⏸ Newmos: en pausa (sin fecha de vuelta)

### 2026-08-31 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hoy toca decidir sobre Golossa, tapar huecos del miércoles y confirmar que Xavi sale mañana.

*Para hoy*
🔔 Golossa: cierre del mes (análisis de métricas, aprendizajes, ideas de septiembre). Estrategia lista, espera tu OK.
🔴 Cobertura: miércoles 02/09 con dos agujeros (Golossa y MSM). Midtown suma otro el martes 01 (corta).
⚠️ Xavi: lanza mañana con 15 posts EN FIRME. Único faltante: 'Xavi explica el proyecto' del dom 06 (Jaume en edición).

*Cómo va lo pendiente*
✅ Xavi (sep) — programado hasta 04/10. 3/semana desde mañana (mar/jue/dom a las 15:00). Solo falta el vídeo del 06.
✅ Jesús Mora — ok hasta 06/09. Esta semana: guiones + logística de grabación.
🔔 Golossa — espera tu OK. Estrategia lista.
🔴 Midtown — 01/09 sin programar. Reunión pendiente del 28/08.
🔴 MSM — 02/09 sin programar.
⏸ Newmos — en pausa.

*Recordatorios*
⚠️ Notas tuyas sin hacer: dos de grabaciones (05/08: Jesús Mora y Golossa) y una sobre proyecto nuevo de análisis (31/07).
⚠️ Bandeja: 17 ideas sin triar (15 llevan +7 días). 9 tienen cliente: con tu OK salen guionizadas esa noche.

Una vez cierres Golossa, nos ponemos con los huecos del miércoles 🙌

- ⚠️ 2026-08-31 00:46 · guionizar: [golossa] Historia con IA: por culpa del producto pasa algo inesperado: es una réplica y no tiene desglose. Escribe 2-3 líneas en Notas (qué pasa, dónde está el giro, por qué funciona) y se guioniza sola la próxima corrida.

### 2026-08-31 00:46 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• Golossa: Que le pasa a tu cuerpo si estas un mes sin comer 
  https://app.notion.com/p/3c7496ca6d5181b1a22bdb0a5cec9073

Toca el enlace para abrirla en Notion 📱

### 2026-08-31 00:46 · DESGLOSE · normal (enviado por: whatsapp)
🎬 No puedo guionizar esto: no puedo abrir la referencia y no sé qué pasa en el vídeo.

• Golossa: Historia con IA: por culpa del producto pasa algo inesperado

Escríbeme 2 líneas de cada una en las Notas: qué pasa, dónde está el giro y por qué funciona. Solo eso — no hace falta tocar el desplegable, se guionizan solas en la siguiente corrida.

Las tienes todas juntas en el panel 🖊️ Falta desglose 🙌

### 2026-09-01 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bandeja para arriba, Xavi arranca hoy y hay 5 huecos sin programar: mucho por desbloquear.

*Para hoy*

🔔 *Bandeja* — 23 sin triar (17 hace más de una semana). 12 tienen cliente y esperan tu OK para guionizarse esa noche.

🔔 *Xavi (2026-09)* — estrategia lista. Hoy sale el teaser (mar 01, 8s, copia mínimo). 15 posts EN FIRME hasta 04/10.

🔴 *Huecos sin programar:*
  • Golossa: mié 02/09 (🎬17)
  • Midtown: mar 01/09 (🎬1)
  • Jesús Mora: dom 13/09 (🎬13)
  • MSM: mié 02/09
  • Xavi: dom 06/09 en borrador (con Jaume; si no llega, ese día no se publica)

*Cómo va lo pendiente*

⏳ Jesús Mora (2026-07) — copies en curso, distrib. en curso. 27/07: Coco escribe copy, primer flujo OK

⏳ Xavi (2026-07) — edición adelantada (56 piezas), espera tu OK en estrategia

⏳ Xavi (2026-09) — 15 posts programados EN FIRME. Hoy teaser, dom 06 todavía en edición

⏳ Golossa — guionizando, lista de tomas y logística pendiente

🟡 Midtown — retoman septiembre (reunión vencida 28/08)

⏸ Newmos — pausa

*Recordatorios*

❌ *Análisis mensuales de agosto* — faltan 5: MidTown, Golossa, Newmos, MSM, Jesús Mora. Brutos en tu correo. ¿Arrancamos el Analista hoy?

⚠️ 4 notas tuyas vencidas:
  • 2026-07-31: Automatizar análisis mensuales de noche
  • 2026-08-05: Grabar con Jesús Mora y Golossa (ok ~12/08)
  • 2026-08-28: Reunión Midtown

Me avisa cuando tengas claro y seguimos 💪

### 2026-09-02 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi tiene 15 posts EN FIRME programados hasta octubre (arranque limpio: teaser ✅, carrusel hoy, presentación mañana). Lo único con fecha y sin material es el 06/09 — edición de Jaume en vilo. Si lo cierra hoy, tranqui; si no, ese domingo entra en blanco.

*Para hoy* 🔔
• Edición Xavi (06/09): si Jaume lo cierra hoy, seguro. Si no, ese domingo sin vídeo.
• Bandeja parada: 23 ideas sin revisar, 12 listas para que guionice Coco si dices que sí.
• Cobertura rota HOY: Golossa + MSM caen mié 02. Midtown jue 03, Jesús Mora dom 13. ¿Qué programamos?
• Análisis mensuales: 5 clientes pendientes (MidTown, Golossa, Newmos, MSM, Jesús Mora). ¿Arranco el Analista?

*Cómo va lo pendiente*
• ⏳ Xavi — 15 posts programados. Teaser (mar 01) + carrusel (hoy) + presentación (mañana) OK. El 06/09 espera edición.
• ⏳ Jesús Mora — grabación toca esta semana. Copies y distribución en marcha. Dom 13 sin contenido.
• ⏳ Golossa — guiones y logística toca esta semana. Mié 02 sin programar.
• ⏳ Midtown — retoman en septiembre. Reunión del 28/08 pendiente. Jue 03 sin programar.
• 🟡 MSM — mié 02 en borrador.
• ⏸ Newmos — en pausa sin fecha de vuelta.

*Recordatorios*
• Notas viejas: 4 avisos del 31/07 al 28/08 (probablemente fuera de plazo). Revisa si hay que tachar.
• Bandeja: las 12 ideas con cliente necesitan tu OK (Estado=Aprobada) para que Coco guionice esta noche.

Cuando quieras seguimos 🙌

### 2026-09-03 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 5 a revisar:

🔴 Golossa: dom 06/09 sin programar · 🎬17
🔴 Midtown: jue 03/09 sin programar · 🎬1
🔴 Jesús Mora: dom 13/09 sin programar · 🎬13
🔴 MSM: dom 06/09 sin programar
🟡 Xavi: dom 06/09 en borrador · 🎬5 ✍️1
⏸ Newmos: en pausa (sin fecha de vuelta)

### 2026-09-03 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Semana apretada: programación a ajustar, Bandeja sin triar y análisis de Agosto pendientes. Lo accionable está limpio.

*Para hoy* 🔔

• Midtown sin programación hoy (1 post). Decidir y meter en Metricool.

• Fin de semana: Golossa (17 posts el 06), MSM (06), Xavi (5 posts + 1 en edición con Jaume — si no cierra, ese domingo no sale nada) y Jesús Mora (13 posts el 13).

• Bandeja: 23 ideas, 12 con cliente ya. Si das OK a esas 12 esta noche, mañana salen guionizadas.

• Análisis de Agosto: 5 clientes. Cuando digas, arrancamos.

*Cómo va lo pendiente*

• ⏳ Jesús Mora (2026-07) — distribución. Último copy: 27/07.
• 🔔 Xavi (2026-07) — estrategia lista, espera tu OK.
• ⏳ Xavi (2026-09) — 15 posts EN FIRME. Todo listo salvo pieza del 06 (edición).
• ⏸ Newmos — en pausa.

*Recordatorios*

Cuatro de agosto sin cerrar:
• ❌ Grabar con Jesús Mora (antes de agotar programación)
• ❌ Grabar con Golossa (idem)
• ⚠️ Reunión Midtown (tocaba retomar septiembre)
• ⚠️ Arrancar análisis mensuales en proyecto nuevo

Cuando decidas sobre programación y Bandeja, seguimos 🙌

### 2026-09-04 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Viernes tranquilo en teoría, pero hay un puñado que no puede esperar.

*Para hoy*

🔔 Análisis de agosto: MidTown, Golossa, Newmos, MSM y Jesús Mora están sin cerrar. Los datos ya están en tu correo. Arranca el Analista en sesión y ciérralo hoy si puede ser — agosto se va.

🔔 Bandeja: 23 ideas paradas, 17 llevan +7 días sin mover. De esas, 12 ya tienen cliente y vídeo: solo les falta que las marques como aprobadas y salen guionizadas esa noche automático. Pásales un ojo rápido si quieres que la fábrica respire.

⚠️ Xavi — dom 06/09: el post de "Xavi explica el proyecto" está en borrador (edición con Jaume). Si no llega a tiempo, ese domingo queda vacío. Es el único detalle del mes.

*Cómo va lo pendiente*

• ✅ Xavi (sept): cubierto al 99%, 15 posts EN FIRME, solo espera ese vídeo del 06
• 🔔 Xavi (julio): tu OK en estrategia (pendiente un tiempo ya)
• ⏳ Jesús Mora: copies y distribución en curso
• ⏳ Golossa: guiones y logística de grabación esta semana
• ⚠️ Midtown: vuelta en septiembre (falta coordinar)
• ⏳ MSM: en marcha
• ⏸️ Newmos: pausa

*Recordatorios*

❌ Vencidas hace demasiados días:
  · Grabar con Jesús Mora y Golossa (notitas del 05/08)
  · Reunión Midtown (28/08, era para coordinar vuelta)
  · Montar un proyecto nuevo para los análisis mensuales (31/07)

🔴 Huecos sin programar:
  · Sáb 05/09 — Midtown
  · Dom 06/09 — Golossa (+ Xavi en borrador)
  · Mié 09/09 — MSM
  · Dom 13/09 — Jesús Mora

Una vez le des el OK a la bandeja, todo se desbloquea. Dale una pasada y me avisa 🙌

### 2026-09-05 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi necesita tu OK ya: el vídeo de mañana está en Metricool (borrador), revísalo y pásalo a firme. Falta el corte de 1 min para Instagram.

*Para hoy* 🔔
• Xavi: revisa y firma el vídeo largo del 06/09 en Metricool (para que salga a las 15:00).
• Ese vídeo: falta el corte de 1 min para IG/TikTok.

Cobertura ajustada: Midtown (hoy), Golossa (mañana), MSM (mié 09) y Jesús Mora (13/09) sin programar.

*Cómo va lo pendiente*
• ✅ Xavi — publica 3/semana desde el 01/09. Mañana necesita tu OK.
• ⏳ Golossa — en guiones (fase 1). Sin programar para el 06/09.
• ⏳ Jesús Mora — ciclo de julio en distribución. Sin programar para el 13/09.
• 🔴 Midtown — hoy sin cobertura. Reunión de agosto pendiente.
• 🔴 MSM — mié 09/09 sin programar.
• ⏸ Newmos — en pausa.

*Recordatorios*
• Bandeja: 24 ideas paradas (17 llevan más de una semana). 12 ya tienen cliente — falta tu OK para salir guionizadas.
• Análisis de agosto: 5 clientes sin cerrar. Datos en el correo.
• Tarea urgente: grabar con Jesús Mora y Golossa antes de que se agote la programación.

### 2026-09-06 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi para hoy: el vídeo largo del dom 06/09 está en Metricool en borrador, sin autopublicar. 🔔 Revisalo y decime si pasa a firme. Falta el corte de 1 min para IG, pero eso lo hacemos después. Se publica a las 15:00 si le das OK.

*Para hoy*
• Bandeja: 🔔 24 ideas sin triar, 12 con cliente y listas para aprobarse (Estado=Aprobada → guionizadas esa noche)
• Huecos próximos: mar 08 (Midtown), mié 09 (Golossa + MSM), dom 13 (Jesús Mora)

*Cómo va lo pendiente*
• ⏳ Xavi — 15 posts en firme hasta 04/10. Hoy, la prueba más gorda. Copies ok, distribución programada.
• ⏳ Golossa — guiones en preparación (toca esta semana), pero mié 09 está vacío.
• ⏳ Jesús Mora — distribución en curso. Cobertura se agota, dom 13 vacío.
• ⏳ Midtown — análisis agosto pendiente, mar 08 sin programar.
• ⏳ MSM — análisis agosto pendiente, mié 09 sin programar.
• ⏳ Newmos — en pausa. Análisis agosto pendiente.

*Recordatorios* ⚠️
• Notas tuyas vencidas — todas de agosto, algunas de hace más de un mes:
  • Dejar corriendo análisis mensuales (31/07)
  • Grabar con Jesús Mora (⚡ alta, vencida 05/08)
  • Grabar con Golossa y confirmar cobertura (⚡ alta, vencida 05/08)
  • Reunión con Midtown (⚡ alta, vencida 28/08)

• Análisis mensuales de agosto: 5 pendientes. Analista listo para arrancar en sesión (brutos en tu correo).

Bastante movida para hoy. Cuando quieras arrancamos 🙌

### 2026-09-07 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 4 a revisar:

🔴 Golossa: mié 09/09 sin programar · 🎬17
🔴 Midtown: mar 08/09 (corta) sin programar · 🎬1
🔴 Jesús Mora: dom 13/09 sin programar · 🎬13
🔴 MSM: mié 09/09 sin programar
⏸ Newmos: en pausa (sin fecha de vuelta)
✅ Xavi: ok hasta jue 17/09 · 🎬5

### 2026-09-07 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres clientes sin programación para mañana. La Bandeja tiene ideas esperando tu OK.

*Para hoy* 🔔
• Midtown (mar 08, corta), Golossa y MSM (mié 09): sin contenido. En la Bandeja hay 24 ideas, 12 ya con cliente — triálas, aprueba y esa noche sale guionizado.
• Xavi: el vídeo largo del dom 06 está en Metricool en borrador desde el 04/09. Revísalo, pásalo a firme. Falta el corte de 1 min para IG.
• Análisis de agosto: 5 sin hacer (MidTown, Golossa, Newmos, MSM, Jesús Mora). Los datos brutos ya deberían estar en correo. Avísame cuándo arrancar el Analista.

*Cómo va lo pendiente*
• 🔴 Golossa (✍️ guiones) — sin programación mañana + grabación urgente (se agota cobertura desde 05/08)
• 🔴 Midtown (retoma sep) — sin programación mañana + tu reunión no se hizo (era 28/08)
• 🔴 Jesús Mora (🎬 grabando) — sin programación dom 13 + grabación urgente (se agota cobertura desde 05/08)
• 🔴 MSM — sin programación mañana
• ⏸ Newmos — en pausa
• ✅ Xavi (distribución) — ok hasta jue 17, pero ese vídeo esperando tu OK

*Recordatorios*
• Grabar con Jesús Mora y Golossa: nota vencida (05/08) y cobertura que se agota. Coordina.
• Reunión Midtown: cuando antes, así activamos el contenido.

Cuando tengas decidido sobre la Bandeja me lo dices 🙌

### 2026-09-08 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres huecos sin programación esta semana, Bandeja atascada, análisis sin hacer. Lo de grabar quedó atrás.

*Para hoy*

🔔 *Xavi (2026-09)* — estrategia lista, espera tu OK. Revisor vídeo largo dom 06/09 en Metricool (borrador, copy listo). Falta corte 1 min para IG.

🔴 *Midtown* — hoy sin programación + reunión retoma (28/08) pendiente.

*Huecos sin programar*
• Golossa — mié 09
• Jesús Mora — dom 13
• MSM — mié 09

*Cómo va lo pendiente*

✅ *Xavi* — 15 posts EN FIRME sep-oct. Espera OK + revisión pieza larga.
⏳ *Golossa* — toca grabar esta semana (reloj). Mié 09 sin programación.
⏳ *Jesús Mora* — edición + programación (reloj). Dom 13 sin programación.
⏸ *Midtown* — retoma sept, sin programación + reunión sin hacer.
⚠️ *MSM* — mié 09 sin programación.
⏸ *Newmos* — pausa.

*Recordatorios*

🔴 *Análisis mensuales*: 5 sin hacer (MidTown, Golossa, Newmos, MSM, Jesús Mora). Brutos en inbox. ¿Arrancamos Analista?

🔴 *Bandeja*: 24 ideas sin triar (23 >7 días). 12 con cliente, solo falta tu OK para guionizar.

⚠️ *Notas vencidas*:
• Grabar JM (ok hasta 12/08)
• Grabar Golossa (confirmar cobertura)
• Reunión Midtown (28/08)

Cuando quieras jalamos 💪

### 2026-09-09 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bastante cosa que decidir hoy, jefe. Los huecos llegan.

*Para hoy* 🔔
• Golossa, MSM: hoy sin programar (mié 09)
• Midtown: mañana sin programar (jue 10) + 1 vídeo listo
• Jesús Mora: dom 13 sin programar + 1 vídeo listo
• 🔔 Bandeja: 24 ideas sin triar (23 llevan +7 días). De esas, 12 ya tienen cliente — solo les falta tu OK (Estado=Aprobada) y se guioniza esa noche.
• 🔔 Análisis agosto: 5 clientes pendientes. Brutos de Metricool listos → arrancar Analista en sesión.

*Cómo va lo pendiente*
• ✅ Xavi — distribución ok hasta dom 20/09. El vídeo del 06/09 en Metricool (revisar y pasar a firme). Solo falta corte de 1 min para IG.
• ⏳ Golossa — grabación toca esta semana
• ⏳ Jesús Mora — edición ok; copies y programación en curso
• ⚠️ Midtown — sin actividad. Nota pendiente: reunión (28/08).
• ⚠️ Newmos — pausa (sin fecha de vuelta)
• ⚠️ MSM — sin actividad

*Recordatorios*
• 4 notas vencidas: análisis mensuales (31/07), grabar Jesús Mora (05/08), grabar Golossa (05/08), reunión Midtown (28/08).

Cuando quieras seguimos 🙌

### 2026-09-09 16:15 · EDICIÓN · urgente (escrito en sesión con Claude Code)
Xavi C01 "El coaching de mierda" alargado: 43s → 83s. El corte viejo se quedaba a mitad de
frase ("pero tienes que haber vivido"); el nuevo cierra en "no puedes aprender de formaciones,
no puedes aprender de titulaciones. **Lo tienes que vivir**".

`/Volumes/DD 2 TB WORK/Xavi Colomina/Videos/Podcast/clips recortados/vertical/C01_coaching-mierda_vertical_v2.mp4`

⚠️ Esa pieza **publica mañana 10/09 a las 15:00 y Xavi va en autopublicación**. En Metricool
sigue el corte de 43s: hay que subir el v2 a Drive y sustituirlo antes de esa hora, o sale el
viejo. El copy no hay que tocarlo.

### 2026-09-10 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 13/09 sin programar
🔴 Newmos: dom 13/09 sin programar
⏸ Midtown: en pausa (sin fecha de vuelta)
✅ Xavi: ok hasta mar 22/09 · 🎬5

### 2026-09-10 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay dos huecos para tapar y una bandeja que espera tu toque.

*Para hoy*

🔔 Xavi: el vídeo largo de dom 06/09 (en Metricool) está en borrador. Échale un ojo y pasa a firme.

🔔 Bandeja: 24 ideas sin clasificar, 12 ya con cliente. Cuando triéis, salen guionizadas esa noche.

🔴 Jesús Mora y Newmos: dom 13/09 sin programar. Hay que currar hoy o se queda en blanco.

*Cómo va lo pendiente*

• ✅ Xavi — ok hasta 22/09
• 🎬 Newmos — grabando, pero sin cobertura para el fin de semana
• ✂️ Jesús Mora — en distribución, falta cobertura para el 13
• ⏸ Midtown — en pausa

*Recordatorios*

• Análisis mensuales: 5 pendientes (MidTown, Golossa, Newmos, MSM, Jesús Mora). Los brutos de Metricool ya deberían estar en tu correo — arrancamos sesión del Analista cuando quieras.
• Midtown: retoman en septiembre. Agendar reunión.

Cuando lo tengas claro me avisas 🙌

### 2026-09-11 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Estrategia de Xavi lista para cerrar. Análisis de agosto espera el bruto. La cobertura empieza a apretarse.

*Para hoy* 🔔
• Xavi (2026-07): ¿vamos con la estrategia?
• Análisis de agosto: ¿ya te llegó el bruto de Metricool? Listo para arrancar el Analista
• Bandeja: 24 ideas, 12 esperan tu aprobación — aprobadas hoy salen guionizadas esta noche
• Cobertura: Jesús Mora y Newmos sin programar para dom 13/09

*Cómo va lo pendiente*
• ✅ Xavi (2026-09) — 15 posts EN FIRME del 01/09 al 04/10, distribución en marcha
• ⏳ Jesús Mora (2026-07) — edición en curso, copies listos, falta cobertura 13/09
• ⏳ Newmos — grabación toca esta semana, falta cobertura 13/09
• ⏸ Golossa, MSM — análisis de agosto pendiente
• ⏸ Midtown — en pausa sin fecha, análisis pendiente

*Recordatorios*
• Tres notas del limbo (todas vencidas):
  – Grabar con Jesús Mora (ok hasta 12/08)
  – Grabar con Golossa (ok hasta 12/08)
  – Reunión Midtown (era 28/08)
• Xavi: vídeo dom 06/09 en Metricool en borrador — revísalo y pásalo a firme. Falta corte 1 min para IG

Dale, cuando hayas decidido me avisa 🙌

### 2026-09-12 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Mañana son dos domingos sin programar (Jesús Mora y Newmos). Eso es lo urgente. Después Xavi.

*Para hoy*
🔴 Jesús Mora: dom 13/09 sin programar
🔴 Newmos: dom 13/09 sin programar
🔔 Xavi — vídeo del 06/09 en Metricool (borrador). Revísalo y pasalo a firme; falta el corte de 1 min para IG.
💡 Bandeja: 24 ideas (12 listas con cliente). OK = guionizadas esta noche.
📊 Agosto: 5 análisis sin cerrar. Brutos listos; sesión Analista cuando quieras.

*Cómo va lo pendiente*
⏳ Xavi (2026-09) — distribución en ritmo, espera tu OK
⏳ Jesús Mora (2026-07) — distribución en curso; *grabación vencida 05/08*
🎬 Newmos — toca grabar esta semana
⚠️ Golossa — parada; *grabación vencida 05/08*
⏸ Midtown — pausa; *reunión vencida 28/08*
❌ MSM — sin novedad

*Recordatorios*
• Dos alarmas: grabar con Jesús Mora y Golossa (vencida 05/08, capacidad se agota).
• Reunión Midtown: vencida hace 2 semanas.

Decime qué hacemos con los domingos 🙌

### 2026-09-13 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Domingo tranquilo pero con un par de avisos que no podemos ignorar.

*Para hoy*
🔴 Newmos: hoy sin cobertura (toca grabar esta semana). O grabáis hoy o programamos algo rápido.
🔴 Jesús Mora: el domingo 20/09 también está sin programa.
🔔 Bandeja: 24 ideas sin triar, 12 ya con cliente y solo esperan tu OK para guionizarse esta noche. Dime cuáles apruebas.
⏳ Análisis de agosto: Midtown, Golossa, Newmos, MSM y Jesús Mora (5). Cuando quieras, arrancamos el Analista.

*Cómo va lo pendiente*
• ✅ Xavi (sept): ok hasta jueves 24/09.
• 🔔 Xavi (julio): estrategia lista, espera tu OK.
• ⏳ Jesús Mora: copies en curso, distribución moviendo. Un programa VR en borrador de Metricool.
• ⏸ Midtown: parada.

*Recordatorios*
La nota sobre reunión con Midtown, y las de grabar con Jesús Mora y Golossa, son de julio-agosto — probablemente obsoletas. Si algo sigue en pie, dímelo.

Cuando tengas claro qué apruebas de la Bandeja, me avisas y soltamos todo 🙌

### 2026-09-14 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 20/09 sin programar
🔴 Newmos: dom 20/09 sin programar
⏸ Midtown: en pausa (sin fecha de vuelta)
✅ Xavi: ok hasta jue 24/09 · 🎬5

### 2026-09-14 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Análisis de agosto pendiente y dos huecos en programación para el fin de semana.

*Para hoy* 🔔

• Analista: arrancar sesión para cierre agosto — faltan 5 clientes (MidTown, Golossa, Newmos, MSM, Jesús Mora).
• Xavi — dom 06/09: revisar borrador de Metricool (sin autopublicar) y pasarlo a firme. Falta corte 1 min para IG.
• Bandeja: 24 ideas llevan más de 7 días. 12 ya tienen cliente: apruébalas para que guionicen.

*Cómo va lo pendiente*

• 🔴 Jesús Mora — dom 20/09 sin programación. Ciclo 2026-07 en curso.
• 🔴 Newmos — dom 20/09 sin programación. Ciclo 2026-09: grabación esta semana.
• ⏳ Xavi — ok hasta jue 24/09 (3/semana). Copies en curso.
• ⏸ Midtown — en pausa. Reunión pendiente del 28/08.
• ⚠️ Golossa — análisis agosto sin hacer.
• ⚠️ MSM — análisis agosto sin hacer.

*Recordatorios*

Tres notas viejas fuera de plazo: proyecto para análisis mensuales (31/07) + grabar Jesús Mora (05/08) + grabar Golossa (05/08).

Avísame cuando arranques.

### 2026-09-15 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hoy toca meter mano en tres frentes: Xavi necesita tu OK en un vídeo, el análisis de agosto está retrasado y la bandeja sigue sin que apruebes nada.

*Para hoy*

🔔 *Xavi — vídeo largo (dom 06/09):* Está en Metricool en borrador, copy y etiquetas listos. Revísalo y pasa a firme cuando quieras. Falta el corte de 1 min para Instagram, pero el resto ya vuela.

🔔 *Análisis de agosto:* Faltan 5 clientes (MidTown, Golossa, Newmos, MSM, Jesús Mora). Los brutos de Metricool deberían estar en el correo. Cuando quieras arrancamos el Analista en sesión.

⚠️ *Bandeja:* 24 ideas llevan más de 7 días sin decidir. 12 ya tienen cliente, solo necesitan "Aprobada" y esa noche Coco las guioniza. Dale paso a lo que te sirva.

*Cómo va lo pendiente*

• ⏳ *Golossa* — análisis agosto sin hacer
• ⏸ *Midtown* — en pausa desde agosto, ¿retoman o no?
• ✅ *Jesús Mora* — ciclo 07 en distribución, análisis sin hacer, grabación pendiente
• 🎬 *Newmos* — toca edición esta semana, falta programar dom 20/09, análisis sin hacer
• ❌ *MSM* — solo falta análisis de agosto
• ✅ *Xavi* — ciclo 09 activo, 15 posts en firme, copies listos, espera tu OK del vídeo

*Recordatorios*

• Dos notas tuyas de grabar (Jesús Mora, Golossa) están vencidas — cuando quieras les damos prioridad
• Cobertura: Jesús Mora + Newmos sin programar el dom 20/09

Cuando quieras me dices y seguimos 🙌

### 2026-09-16 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi tiene algo esperando tu OK en Metricool, el resto es más de follow-up.

*Para hoy*

🔔 *Xavi — vídeo 06/09*: ya en Metricool en borrador, sin autopublicar. Revisar y pasar a firme. Falta el corte de 1 min para IG.

🔴 *Huecos*: dom 20/09 sin cobertura en Jesús Mora y Newmos. Si tienes algo para meterles, avisa antes del miércoles.

📊 *Análisis mensuales*: faltan 5 (MidTown, Golossa, Newmos, MSM, Jesús Mora). Brutos de agosto deberían estar. Cuando quieras, lanzo al Analista.

🔔 *Bandeja*: 24 ideas paradas hace >7 días. 12 tienen cliente pero esperan tu OK (Estado=Aprobada) para guionizar esa noche.

*Cómo va lo pendiente*

⏳ Xavi (sept) — edición ok, copies en curso, programado hasta 27/09
⏳ Jesús Mora (julio) — distribución en curso, copies andando
⏳ Newmos — edición/QA/programación (toca esta semana)
⏸ Midtown — pausa, retorno sin confirmar
❓ Golossa, MSM — nada nuevo visible

*Recordatorios*

Tienes 3 notas sin cerrar (no sé si se hicieron o qué):
• Grabar con Jesús Mora — plazo 12/08 (hace un mes)
• Grabar con Golossa — plazo 05/08 (idem)
• Reunión Midtown — 28/08 (tampoco se hizo)

Avisa si necesitan acción o si las dejas.

### 2026-09-17 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 20/09 sin programar
🔴 Newmos: dom 20/09 sin programar
⏸ Midtown: en pausa (sin fecha de vuelta)
✅ Xavi: ok hasta mar 29/09 · 🎬5

### 2026-09-17 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bastante para hoy — un hueco de programación para este domingo y análisis pendientes.

*Para hoy* 🔔
• Xavi: vídeo largo dom 06/09 en Metricool en borrador (copy, títulos, etiquetas listos). Revísalo y pásalo a firme. Solo falta corte de 1 min para IG.
• Análisis de agosto: arrancar Analista en sesión — faltan Golossa, Newmos, MSM, JM y Midtown. Brutos de Metricool ya deberían estar en el correo.
• Cobertura: Jesús Mora y Newmos sin programación para dom 20/09.

*Cómo va lo pendiente*
• ✅ Xavi — 51 piezas listas, 15 posts EN FIRME del 01/09 al 04/10. Cadencia mar/jue/dom ok.
• ⏳ Newmos — edición/programación en marcha; sin cobertura el domingo.
• ⏳ Jesús Mora — análisis en marcha; sin cobertura el domingo.
• ⏸ Midtown — pausa sin fecha de vuelta.

*Recordatorios*
• Bandeja: 24 ideas paradas (más de 7 días). 12 con cliente asignado — esperan aprobación para guionizar esa noche.
• ⚠️ Cuatro notas vencidas: análisis automáticos (31/07), grabar JM (05/08), grabar Golossa (05/08), reunión Midtown (28/08). Archivamos o retomamos?

Cuando quieras seguimos 🙌

### 2026-09-18 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay un hueco en Newmos para dom 20 (EN 2 DÍAS): toca edición + programación.

*Para hoy* 🔔
• *Newmos*: ¿vídeo montado, o nos metemos fin de semana?
• *Xavi (2026-09)*: grabación semana 3. ¿Cuándo?
• *Bandeja*: 16 ideas listos para guionizarse EN FIRME si les das OK.
• *Análisis agosto*: 5 brutos en el correo. ¿Arrancar el Analista?

*Cómo va lo pendiente*
• ✅ *Xavi (2026-09)* — edición adelantada, copys en curso. Ok hasta 29/09.
• ⏳ *Xavi (2026-07)* — en distribución, espera tu OK en estrategia.
• ⏳ *Newmos* — sem 3 = edición+programación. Material sin ciclo visible.
• ⏳ *Jesús Mora (2026-07)* — análisis semana 3 + dom 27 sin cubrir.
• ⚠️ *Golossa, Midtown, MSM* — análisis agosto.

*Recordatorios*
• Notas sin hacer: todas viejas (ago). Midtown en pausa sin retorno.

Dale cuando quieras. 🙌

### 2026-09-19 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tenés dos urgencias hoy y más decisiones de las que parece.

*Para hoy* 🔔

• Newmos: dom 20/09 sin programar (mañana).
• Xavi: vídeo del 06/09 en borrador, esperando tu OK para pasar a firme.
• Análisis de agosto: faltan 5 de 6. Necesito que arranques el Analista en sesión (brutos en correo).
• Bandeja: 28 ideas esperan tu OK. 16 ya están asignadas — si das luz, esa noche salen guionizadas.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — copies/distribución en curso. Dom 27/09 sin programar.
• Xavi — ciclo 2026-07 espera tu OK en estrategia. 2026-09 cubierto hasta jue 01/10.
• ⏳ Newmos — toca edición/programación, empezando por mañana.
• ⏸ Midtown — pausa (reunión tuya del 28/08 pendiente).
• ❌ Golossa — nota sin hacer: grabar antes de agotar programación (⚡ alta, vencida).
• ⏳ MSM — en lista de análisis agosto.

*Recordatorios*

• 4 notas tuyas sin hacer (todas vencidas). Dos ⚡ alta: grabar Jesús Mora y Golossa.
• Xavi 2026-07 esperando desde hace.

La bandeja es lo que más mueve hoy — aprueba esas 16 y esa noche se desatasca 🚀

### 2026-09-20 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Newmos sin contenido hoy y la Bandeja desbordada. Dos decisiones necesarias.

*Para hoy*
🔔 Newmos — dom 20/09 sin programar (es HOY). Toca edición y programación: vídeo, copy y luz verde para Metricool.
🔔 Bandeja — 28 ideas sin triar (16 ya tienen cliente, solo les falta Estado=Aprobada). 24 llevan más de una semana; si las apruebas, esa noche se guionizan.

*Cómo va lo pendiente*
• ✅ Xavi — 15 posts EN FIRME hasta 04/10. El vídeo del 06/09 ya en Metricool (revisar y pasar a firme). Corte de 1 min para IG sin material.
• 🔴 Jesús Mora — dom 27/09 sin programar; la semana que viene igual que Newmos hoy.
• ⚠️ Golossa, MSM, Newmos — análisis de agosto sin hacer.
• ⏸ Midtown — pausa. Reunión pendiente.

*Recordatorios*
Notas sin hacer: grabar con Jesús Mora y Golossa (se acerca el corte), reunión Midtown. Las fechas pasaron pero los encargos siguen ahí.

Tú mandas 💪

### 2026-09-21 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 27/09 sin programar
🔴 Newmos: dom 27/09 sin programar
⏸ Midtown: en pausa (sin fecha de vuelta)
✅ Xavi: ok hasta jue 01/10 · 🎬5

### 2026-09-21 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres cosas accionables hoy.

*Para hoy*

🔔 *Bandeja*: 28 ideas, 16 ya tienen cliente. Aprueba estas 16 esta mañana en la Bandeja y se guionizarán esta noche.

🔔 *Dom 27/09 (en 6 días)*: Falta cobertura en Jesús Mora y Newmos. Decide qué va en cada uno para que podamos grabar a tiempo esta semana.

⚠️ *Xavi — vídeo dom 06/09*: En Metricool en borrador, bloqueado (porque autopublica). Revísalo y pásalo a firme. Falta el corte de 1 min para IG.

*Cómo va lo pendiente*

• ✅ Xavi — cubierto hasta jue 01/10, edición lista, copies en curso. Esta semana toca grabación.
• ⏳ Newmos — edición + programación. Dom 27/09 sin cobertura.
• ⏳ Jesús Mora — toca análisis y decidir ideas de octubre. Dom 27/09 sin cobertura.
• ⏸ Midtown — en pausa sin fecha de vuelta.
• ❌ Golossa — sin ciclo desde hace meses.
• ❌ MSM — inactivo.

*Recordatorios*

Nada más urgente. El resto va como está.

Avísame cuando apruebes la bandeja 👍

### 2026-09-22 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Dos huecos sin llenar, ideas paradas esperando tu OK y un vídeo que revisar en Metricool.

*Para hoy*

• ⚠️ Dom 27/09 está hueco en Jesús Mora y Newmos — decide si metemos algo o lo dejamos vacío
• 🔔 Xavi (2026-07): estrategia lista, espera tu OK
• ⚠️ Bandeja: 18 ideas sin triar. 6 ya tienen cliente, solo falta que digas "sí" para guionizarse esta noche (14 llevan más de una semana clavadas)
• 🔔 Xavi (2026-09): vídeo del 06/09 en Metricool en borrador → revisalo y pasalo a firme

*Cómo va lo pendiente*

• ⏳ Jesús Mora — copies y distribución en curso. Copy de 27/07 listo para borrador
• ⏳ Newmos — esta semana: leer métricas de sept, escribir aprendizajes e ideas del siguiente
• ✅ Xavi (2026-07) — edición adelantada. 56 piezas + podcast sin montar
• ✅ Xavi (2026-09) — 51 piezas en bancos, 15 posts EN FIRME hasta 04/10

*Recordatorios*

• Nota sin hacer desde 31/07: "análisis mensuales en proyecto nuevo"
• Si das luz verde a las 6 ideas de la Bandeja, se guionizarán esta noche

Cuando quieras me dices 🙌

### 2026-09-23 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Lo que te espera hoy es poco pero hay un punto de decisión en Xavi que va rápido.

*Para hoy*

🔔 *Xavi — vídeo dom 06/09*: en Metricool en borrador, esperando tu OK para pasar a firme. Falta también el corte de 1 min para IG.

🔴 *Cobertura*: Jesús Mora y Newmos sin nada para dom 27/09. Queda tiempo, pero marca la agenda.

*Cómo va lo pendiente*

⏳ *Jesús Mora* — copies en curso, distribución corriendo.

⏳ *Newmos* — toca esta semana: analizar métricas de septiembre, escribir aprendizajes y sacar ideas para octubre. Dom 27 sin programar.

✅ *Xavi* — 15 posts EN FIRME del 01/09 al 04/10. Edición lista excepto corte para IG.

*Recordatorios*

⚠️ *Bandeja parada*: 18 ideas sin clasificar (14 llevan más de 7 días). De esas, 6 ya tienen cliente — solo necesitan Estado=Aprobada y esa noche salen guionizadas por Coco. Si tienes un rato, triálas rápido: es lo que mueve todo.

⚠️ *Nota pendiente tuya*: dejar corriendo los análisis mensuales en proyecto nuevo. Ya va tarde (31/07) — lo toco cuando digas.

Cuando quieras me dices y seguimos 🙌

### 2026-09-23 01:33 · OLI · normal (enviado por: whatsapp+email)
🤖 Oli ha preparado 8 ideas para NewMos. Hay que revisarlas.

• Demostración en directo: la máquina funcionando en un servicio real, no explicada a cámara  (— · Producto)
• Antes y después: el mismo servicio con y sin el equipo adecuado, cronometrado  (Comparación · Producto)
• Lo que diferencia una extracción/campana bien instalada de una que solo 'cumple'  (— · Educativa)
• Dos soluciones Newmos para el mismo cuello de botella: cuál encaja mejor según el servicio  (Comparación · Producto)
• Un día con el técnico instalador de Newmos, desde dentro  (— · Detrás de cámaras)
• El error más caro al comprar equipo de cocina profesional (y cómo evitarlo)  (— · Storytelling)
• El montaje de una máquina Newmos, de la caja al servicio, sin una palabra  (— · Producto)
• Aleix o Jaume cuentan, a cámara, un pedido que cambió cómo trabaja un cliente  (— · Storytelling)

2 son apuestas ciegas (sin datos detrás).

Apruébalas o descártalas en Notion antes del domingo (el lunes empiezan los guiones). Si descartas una, escribe el motivo en Notas: Oli lo lee el mes que viene.

👉 https://www.notion.so/1a033425f19546edbccdb29b2e6163bb?v=3e3496ca6d518180bf98000c74142ac8

### 2026-09-24 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 3 a revisar:

🔴 Jesús Mora: dom 27/09 sin programar
🔴 Newmos: dom 27/09 sin programar
🔴 Xavi: mar 06/10 sin programar · 🎬5

### 2026-09-24 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Dom 27/09, mar 06/10 sin programa. Bandeja con 26 ideas paradas. Pero lo gordo: análisis mensuales desde 31/07, sin hacer.

*Para hoy*

🔔 *Programación*: dom 27/09 sin material para Jesús Mora, Newmos y Xavi. Mar 06/10 igual para Xavi.

🔔 *Bandeja*: 26 ideas paradas (14 con cliente). Si das OK, salen guionizadas esa noche.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — en distribución, Coco escribe los copies. Flujo probado.
• ⏳ Newmos — toca analizar esta semana.
• ⏳ Xavi — distribución en marcha, 15 posts listos para revisar (01/09-04/10).

*Recordatorios*

• Análisis mensuales: desde 31/07 sin tocar. ¿La lanzamos?

Dale cuando quieras 🙌

### 2026-09-25 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Cuatro decisiones para hoy: dos de Xavi, cobertura y la Bandeja.

*Para hoy* 🔔

• Xavi (2026-07): estrategia espera tu OK. ¿Dale luz?
• Xavi (2026-09): vídeo largo del 06/09 en borrador en Metricool — revísalo para pasar a firme. (Falta corte de 1 min para IG, eso sale cuando confirmes.)
• Cobertura: 3 huecos sin programar
  • dom 27/09 (Jesús Mora)
  • dom 27/09 (Newmos)
  • mar 06/10 (Xavi)
• Bandeja: 26 ideas, 14 ya con cliente — apruébalas y salen guionizadas esta noche.

*Cómo va lo pendiente*

• ⏳ Jesús Mora (2026-07) — distribución en marcha, copies en curso
• ⏳ Newmos — cierre del mes (métricas lisas)
• ⏳ Xavi (2026-07) — 56 piezas en inventario, edición adelantada, espera tu OK en estrategia
• ⏳ Xavi (2026-09) — 51 piezas, 15 posts EN FIRME, copies hechos, pendiente revisar el 06/09

*Recordatorios*

• Nota del 31/07 sobre análisis mensuales en proyecto nuevo: ¿sigue en pie? Si sí, me avisa y lo ponemos en marcha.

Dale que sale 💪

### 2026-09-26 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres cosas que decidir hoy, nada que queme pero visible.

*Para hoy* 🔔

• *Bandeja*: 26 ideas paradas, 18 llevan más de una semana. Las 14 que ya tienen cliente se guionizarán solos esta noche si les marcas Estado=Aprobada — el resto se queda congelado.

• *Cobertura sin material*: Jesús Mora y Newmos sin programación para dom 27/09. Xavi tampoco tiene jue 08/10. ¿Publican algo o dejamos vacío?

• *Xavi, vídeo del 06/09*: Está en Metricool (45s), borrador, con copy y etiquetas. Listo para pasar a firme. Dale OK cuando quieras. (El corte de 1 min para IG sigue esperando vídeo.)

*Cómo va lo pendiente*

• ⏳ Jesús Mora — guionización en marcha, distribución activa. Toca esta semana cerrar la lista de tomas y logística.
• ⏳ Newmos — análisis mensual pendiente de revisar. Métricas del mes claras, lista de ideas para octubre.
• ⏳ Xavi — edición completa, copies rodando, 15 posts EN FIRME salidos del 01/09. Viendo cómo rinden los primeros.

*Recordatorios*

• Tu nota del 31/07 sobre proyectos nuevos para análisis automático → ¿la reciclamos o la dejamos?
• *Aviso de sistema*: si la Bandeja se queda sin triaje, todo sigue en silencio pero nada avanza. Es invisible para el ojo: por eso lo cuento aquí.

Cuando quieras me dices 🙌

### 2026-09-26 10:00 · OLI · normal (enviado por: whatsapp+email)
⏰ Quedan ideas de Oli sin revisar:

• NewMos: 8

El lunes empiezan los guiones: lo que no esté aprobado no se guioniza.

👉 https://www.notion.so/1a033425f19546edbccdb29b2e6163bb?v=3e3496ca6d518180bf98000c74142ac8

### 2026-09-27 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bandeja ancha pero congelada. 26 ideas sin triiar, 14 ya tienen cliente y solo esperan tu OK para guionizarse. Además faltan 3 huecos en la programación.

*Para hoy*
🔔 Xavi 2026-07: estrategia esperando tu OK
🔔 Bandeja: 14 ideas con cliente listas para guionizar, solo falta tu "Aprobada"
⏳ 3 huecos sin programar los próximos días

*Cómo va lo pendiente*
✅ Xavi 2026-09: distribución en marcha, 15 posts EN FIRME hasta el 04/10. Vídeo largo del 06/09 en Metricool en borrador (revisar y pasar a firme)
⏳ Jesús Mora 2026-07: copies en curso. Copy de Coco ya escrito para el 29/07
📊 Newmos: toca análisis de septiembre esta semana

*Recordatorios*
• Bandeja: 26 ideas sin triiar, 18 llevan +7 días. Con tu "Aprobada" en las 14 con cliente, Coco las guioniza automático esa noche
• Nota suya sin hacer: análisis mensuales en proyecto nuevo (📅 31 julio)
• Cobertura: dom 27 (Jesús Mora), dom 04/10 (Newmos), jue 08/10 (Xavi)

Cuando le des luz a la Bandeja, se desbloquea todo 🙌

### 2026-09-28 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 3 a revisar:

🔴 Jesús Mora: mié 30/09 sin programar
🔴 Newmos: dom 04/10 sin programar
🔴 Xavi: jue 08/10 sin programar · 🎬5

### 2026-09-28 00:32 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres huecos sin cerrar (Jesús Mora mié 30/09, Newmos dom 04/10, Xavi jue 08/10) y 26 ideas paradas en la Bandeja, 18 de ellas hace > 7 días.

*Para hoy* 🔔
• Las 14 con cliente se guionizarán esta noche en cuanto las apruebes.
• El resto espera que decidas: ¿sí, no, después?
• Programa los 3 huecos de cobertura.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — copy de 27/07 escrito, en distribución. Falta programar mié 30/09.
• ⏳ Newmos — toca análisis mensual. Falta dom 04/10.
• ✅ Xavi — 15 posts en firme. Vídeo del 06/09 en Metricool en borrador. 🔔 Necesita OK para pasar a firme. Falta jue 08/10.

*Recordatorios*
• ⚠️ Nota de análisis mensuales (31/07): sigue vencida, necesitas arrancar eso en proyecto nuevo.
• ⚠️ Xavi 2026-07: estrategia en stand-by desde hace ~1 mes, espera tu OK.

Dale, cuéntame si necesitas algo 🙌

### 2026-09-29 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Dos huecos de publicación que llegan esta semana y una decisión de Xavi que sigue en pausa.

*Para hoy*

🔔 Cobertura — dos días sin nada programado:
• Mié 30/09 (Jesús Mora)
• Dom 04/10 (Newmos)
Dime qué va en cada uno y lo programamos ya.

🔔 Xavi (2026-07): estrategia lista, espera tu OK. Te la dejé en la carpeta de trabajo.

⚠️ Xavi (2026-09): el vídeo largo del dom 06/09 está en borrador en Metricool desde hace 25 días. Necesita que lo revises y lo firmes. Falta el corte de 1 min para IG si lo quieres.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — copies en curso, distribución en curso
• 📊 Newmos — toca analizar métricas esta semana
• ✅ Xavi (2026-09) — edición lista, 15 posts programados, copies en curso

*Recordatorios*

• Bandeja: 26 ideas paradas (14 con cliente, solo faltan tu Aprobada)
• ⚠️ Nota sin hacer: "análisis mensuales en proyecto nuevo" (desde el 31/07)

Cuando tengas claro qué metes en esos huecos me lo dices y lo dejo todo listo 🙌

### 2026-09-30 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hoy hay dos cosas con las que lidiar: huecos de programación y la Bandeja parada.

*Para hoy* 🔔
• ⚠️ Jesús Mora — *sin programación para hoy* (mié 30/09). Ciclo julio en distribución.
• ⚠️ Newmos — *dom 04/10 sin cobertura*. Semana de análisis; tú dices si metemos algo o esperamos.
• 🔔 Xavi — vídeo largo (06/09) en borrador en Metricool. Revisar y firmar.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — guiones y cierre de logística esta semana.
• 📊 Newmos — análisis de mes + ideas del próximo.
• ✂️ Xavi — edición cubierta hasta el 11/10. Pendiente QA del largo.

*Recordatorios*
• Vídeo de Xavi: falta el corte de 1 min para IG.
• Bandeja: 26 ideas llevan +7 días sin triar. 14 tienen cliente; con tu OK salen guionizadas esta noche.
• Análisis mensuales (nota 31/07): ¿arrancamos?

Avísame cuando cierres lo de hoy y seguimos. 🙌

### 2026-10-01 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 04/10 sin programar
🔴 Newmos: dom 04/10 sin programar
✅ Xavi: ok hasta mar 13/10 · 🎬5

### 2026-10-01 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi sigue esperando tu OK (en estrategia 2026-07), la Bandeja tiene 26 ideas sin triar y el análisis de sept no arranca solo.

*Para hoy* 🔔

• *Xavi (2026-07)*: ok en estrategia, solo espera tu revisión y aprobación
• *Cobertura*: dom 04/10 sin programar en Jesús Mora y Newmos — ¿los programamos?
• *Análisis de sept*: falta hacer en Newmos y Jesús Mora. Los brutos de Metricool ya están en el correo. Cuando quieras, arranco al Analista en sesión.

*Cómo va lo pendiente*

• ⏳ *Jesús Mora (2026-07)*: copies en curso, distribución en curso. Esta semana toca grabación.
• 🔔 *Xavi (2026-07)*: estrategia lista, edición adelantada. Esperando tu OK.
• ✅ *Xavi (2026-09)*: cobertura ok hasta 13/10, copias en curso, distribución programada.
• ⏳ *Newmos*: en guiones y preparación. De las 26 ideas en Bandeja, 14 ya tienen cliente asignado (solo falta que digas "aprobada" para que Coco las guionice esa noche).

*Recordatorios*

• ⚠️ Nota tuya de 31/07 sin tocar: "Dejar corriendo por la noche los análisis mensuales en un proyecto nuevo"

Cuando quieras me dices 🙌

### 2026-10-02 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Viernes, y hay tres cosas que necesitan tu OK.

*Para hoy*
• 🔔 Xavi (2026-07): tienes la estrategia lista, dale el OK
• 🔔 Programación: Jesús Mora y Newmos sin nada para el dom 04/10. Necesitamos qué entra
• Bandeja: 26 ideas sin triar. De esas, 14 tienen cliente — si les das Estado=Aprobada, salen guionizadas esta noche

*Cómo va lo pendiente*
• ⏳ Jesús Mora (2026-07) — copies y distribución en curso, pero el dom 04 sin programar
• ⏳ Newmos — semana de guiones y prep. Dom 04 también sin material
• ⏳ Xavi — 2026-09 ok hasta el 13/10. Toca análisis de septiembre y decidir octubre. 🔔 Espera tu OK en estrategia de 2026-07

*Recordatorios*
• Análisis de septiembre: faltan 5 (MidTown, Golossa, Newmos, MSM, Jesús Mora). Brutos en el correo
• Nota vieja: dejar corriendo análisis mensuales por la noche (31 de julio). Sigue pendiente
• Xavi: vídeo largo del 06/09 en Metricool en borrador. Revisar y pasar a firme

Cuando quieras, me dices 🙌

### 2026-10-03 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tienes 3 frentes hoy: Xavi sigue en espera, huecos de cobertura que se cierran mañana, y análisis de septiembre.

*Para hoy* 🔔

• *Xavi (2026-07)*: estrategia lista desde agosto, necesita tu OK.
• *Análisis de septiembre*: arrancar sesión del Analista (brutos en correo).
• *Cobertura dom 04/10* — tres ajustes:
  • Newmos: dom sin programar
  • Jesús Mora: falta IG o TikTok
  • Xavi: hora mal (no 15:00)
• *Bandeja*: 26 ideas sin triar. 14 tienen cliente: apruébalas y salen guionizadas al rato.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — grabando, distribución en curso.
• ⏳ Newmos — guiones + prep logística. Ideas paradas en Bandeja.
• ⏳ Xavi (2026-07) — inventario validado, espera tu OK en estrategia.
• ✅ Xavi (2026-09) — edición lista, copies en curso, distribución programada.

*Recordatorios*

• Nota tuya sin hacer: meter análisis mensuales en proyecto nuevo (📅 2026-07-31).

Cuando quieras me dices y seguimos 🙌

### 2026-10-03 10:00 · OLI · normal (enviado por: whatsapp+email)
⏰ Quedan ideas de Oli sin revisar:

• NewMos: 8

El lunes empiezan los guiones: lo que no esté aprobado no se guioniza.

👉 https://www.notion.so/1a033425f19546edbccdb29b2e6163bb?v=3e3496ca6d518180bf98000c74142ac8

### 2026-10-04 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi con OK pendiente, Bandeja bloqueada, cobertura del dom rota.

*Para hoy*
🔔 Xavi (2026-07): estrategia lista, espera tu OK.
🔔 Bandeja: 26 ideas hace más de una semana sin triar. 14 llevan cliente asignado — tu Aprobada y salen guionizadas mañana solo.
🔴 Cobertura hoy: Newmos sin nada · Jesús Mora falta una red · Xavi hora desajustada (15:00 es lo correcto).

*Cómo va lo pendiente*
• ⏳ Xavi (2026-07) — 56 piezas inventario, espera OK en estrategia.
• ⏳ Xavi (2026-09) — 51 piezas listas. 15 posts EN FIRME 01/09→04/10. Falta corte de 1 min IG del 06/09.
• ⏳ Jesús Mora — copy del 27/07 escrito. Hoy toca grabación.
• ⏳ Newmos — guionizar y prep rodaje hoy. Sin material en cobertura.

*Recordatorios*
• Análisis septiembre (Newmos, Jesús Mora) en sesión — datos de Metricool ya en el email.
• Tu nota: arrancar análisis por la noche (📅 31/07).

Cuando quieras me dices y seguimos 🙌

### 2026-10-05 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: mié 07/10 sin programar
🔴 Newmos: dom 11/10 sin programar
✅ Xavi: ok hasta jue 15/10 · 🎬5

### 2026-10-05 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
14 ideas esperan tu OK para dispararse, y hay dos huecos de cobertura para llenar esta semana.

*Para hoy* 🔔
• Cobertura: mié 07/10 (Jesús Mora) y dom 11/10 (Newmos) sin programar. Tú decides qué piezas.
• Bandeja: 14 de 26 ideas tienen cliente, solo esperan tu "Aprobada" para salir guionizadas esa noche.

*Cómo va lo pendiente*
• ⏳ Xavi — analizar septiembre (métricas, aprendizajes, ideas de octubre).
• ⏳ Newmos — guiones y logística de grabación; sin cobertura para dom 11/10.
• ⏳ Jesús Mora — grabación esta semana en el taller; sin cobertura para mié 07/10.

*Recordatorios*
• Análisis de septiembre: faltan Newmos y Jesús Mora (la lista que tengo trae ex-clientes, a ver si la hay que limpiar).
• Nota muy vieja: proyecto nuevo para análisis mensuales automáticos de madrugada (desde julio, a lo mejor ya no aplica).

Dime cuándo vamos con los huecos de cobertura o si arrancamos análisis 🙌

### 2026-10-06 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bastante para validar hoy, pero lo que frena todo es la Bandeja: 32 sin OK, 26 con >7 días.

*Para hoy*
• 🔔 Bandeja: 20 ideas con cliente listos, necesitan tu OK para que Coco los escriba esta noche (Newmos depende)
• 🔔 Xavi 2026-07: estrategia hecha, espera tu OK
• ❌ Sin programar: Jesús Mora (mié 07/10) y Newmos (dom 11/10)

*Cómo va lo pendiente*
• ⏳ Jesús Mora: 2026-07 distribuyendo sin cobertura mañana
• ⏳ Newmos: en guiones, esperando Bandeja
• ⏳ Xavi: 2026-07 listo (OK tuyo), 2026-09 copies en marcha

*Recordatorios*
• Análisis de septiembre: Golossa, Midtown, MSM, Newmos y Jesús Mora

OK de la Bandeja y la fábrica mueve esta noche 🙌

### 2026-10-07 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Dos huecos en la programación hoy y el domingo. La Bandeja de ideas sigue esperando tu OK.

*Para hoy*
• 🔔 Mié 07/10 (Jesús Mora) y dom 11/10 (Newmos): sin vídeos programados.
• 🔔 Bandeja: 32 ideas sin triar (20 ya con cliente; esperan tu OK para guionizar).
• 🔔 Xavi (2026-07): espera tu OK en estrategia.

*Cómo va lo pendiente*
• 🎬 Jesús Mora — grabación esta semana; hoy vacío.
• ✍️ Newmos — guiones y prep; dom 11 vacío.
• 📊 Xavi — análisis en curso; distribución hasta dom 18.

*Recordatorios*
• Análisis mensual de septiembre (Gerard) sin hacer. Nota pendiente tuya: arrancar los análisis en proyecto nuevo — el email de Metricool ya debería estar en tu correo.

### 2026-10-07 01:35 · OLI · normal (enviado por: whatsapp+email)
🤖 Oli ha preparado 8 ideas para Xavi Colomina. Hay que revisarlas.

• El detalle de la muñeca en la volea que nadie corrige  (Explicación · Oficio)
• ¿Por qué pierdo el punto justo cuando subo a la red?  (Explicación · Oficio)
• Te han dicho que juegues siempre cruzado. Es mentira.  (Explicación · Oficio)
• Especializarte en un lado te está limitando (y no lo sabes)  (Tips · Oficio)
• Una sesión real de entreno con Xavi, sin cortes de guion  (Vlog / Crónica de evento · Día de trabajo)
• Resumen del domingo: lo último de EL RETO, desde dentro  (Explicación · Producto)
• Corrijo en directo el gesto que te frena en el remate  (Explicación · Oficio)
• Opinión sin pista de fondo: lo que de verdad decide un punto, dicho a cámara y nada más  (Explicación · Opinión)

1 son apuestas ciegas (sin datos detrás).

Apruébalas o descártalas en Notion antes del domingo (el lunes empiezan los guiones). Si descartas una, escribe el motivo en Notas: Oli lo lee el mes que viene.

👉 https://www.notion.so/1a033425f19546edbccdb29b2e6163bb?v=3e3496ca6d518180bf98000c74142ac8

### 2026-10-08 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 2 a revisar:

🔴 Jesús Mora: dom 11/10 sin programar
🔴 Newmos: dom 11/10 sin programar
✅ Xavi: ok hasta mar 20/10 · 🎬5

### 2026-10-08 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
La Bandeja te tiene 40 ideas sin triar (26 llevan más de 7 días). La clave: 28 ya tienen cliente asignado y solo esperan tu aprobación para guionizarse esa noche.

*Para hoy*

🔔 Xavi (ciclo 2026-07): estrategia espera tu OK. Hay 56 piezas, salen a 3-4 por semana desde septiembre. Toca esta semana: guiones + logística de grabación.

🔔 Xavi (ciclo 2026-09): el vídeo largo del dom 06/09 está en Metricool en borrador. Revisar y pasar a firme cuando veas.

🔴 Huecos sin programar: Jesús Mora y Newmos tienen dom 11/10 sin cobertura.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — ciclo 2026-07 en edición/distribución (copies en curso). Dom 11/10 pendiente.
• ⏳ Newmos — ciclo 2026-10 en grabación (toca esta semana). Dom 11/10 pendiente.
• 🔔 Xavi — ciclo 2026-07 bloqueado en tu OK de estrategia. Ciclo 2026-09: toca a editor, vídeo en borrador.

*Recordatorios*

• ⚠️ Análisis de setembre: 5 clientes pendiente (MidTown, Golossa, Newmos, MSM, Jesús Mora).
  Tu nota: arrancar proyecto nuevo para correr los análisis de noche.

Cuando quieras me dices qué aprobamos y seguimos 🙌

### 2026-10-09 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Hay mucho que validar hoy: bandeja parada, tres huecos sin programar y un vídeo esperando OK de Xavi.

*Para hoy* 🔔
• Xavi (2026-07): espera tu OK en estrategia.
• Xavi (2026-09): vídeo del 06/09 en borrador de Metricool — revisar y pasar a firme.
• Tres domingos sin contenido (11/10): Jesús Mora, Newmos y Xavi. Se solapan con edición de Jesús y copys de Xavi.
• Bandeja: 40 ideas sin triar (26 llevan +7 días). 28 tienen cliente asignado — solo esperan tu OK (Estado=Aprobada) para guionizarse esa noche.

*Cómo va lo pendiente*
• ⏳ Jesús Mora (2026-07): copy → vídeo en Metricool, primer test del flujo. Edición esta semana.
• ⏳ Newmos: grabación esta semana.
• ⏳ Xavi (2026-09): distribución en marcha (3/semana), colchón hasta enero. Esperando tu OK en el vídeo del 06.
• ⏳ Xavi (2026-07): inventario validado (56 piezas), editor OK. Espera estrategia aprobada.

*Recordatorios*
• Nota pendiente: automatizar análisis mensuales de noche (31/07).
• Septiembre: faltan análisis de Midtown, Golossa, Newmos, MSM y Jesús Mora. (Los tres primeros ya ex-clientes.)
• 9 creadores de referencia de IG sin @: cuestión de 2 minutos (Jesús Mora y RM Agency).

Cuando quieras seguimos 🙌

### 2026-10-09 00:45 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 1 idea(s), listas para grabar:

• NewMos: La avería que pudo cerrar un restaurante
  https://app.notion.com/p/3f3496ca6d5181dfa7fcf34a55fb8a22

Toca el enlace para abrirla en Notion 📱

### 2026-10-10 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
40 ideas esperando en la Bandeja y tres días sin cobertura.

*Para hoy* 🔔
• Bandeja: 28 tienen cliente → apruébalas y se guionizan solas esa noche. (Las otras 12, tríalas cuando tengas.)
• Xavi (ciclo 07): espera tu OK en estrategia.
• Cobertura: Jesús Mora 14/10, Xavi 11/10, Newmos 18/10 sin nada.

*Cómo va lo pendiente*
• ⏳ Jesús Mora — ciclo 07 en edición+copia (14/10 hueco)
• 🎬 Newmos — grabando (18/10 sin programar)
• ⏳ Xavi — 07 espera OK, 09 en distribución (11/10 hueco)

*Recordatorios*
• Creadores de referencia: 9 sin @creador en Notion. Pestaña «✍️ Falta el @» en 🎯 Creadores: cambias el nombre de cada fila y listo.
• Análisis de setembre: faltan Newmos y Jesús Mora. Arrancamos cuando quieras.

Dime qué haces con la Bandeja y seguimos 🙌

### 2026-10-10 10:00 · OLI · normal (enviado por: whatsapp+email)
⏰ Quedan ideas de Oli sin revisar:

• Xavi Colomina: 8
• NewMos: 8

El lunes empiezan los guiones: lo que no esté aprobado no se guioniza.

👉 https://www.notion.so/1a033425f19546edbccdb29b2e6163bb?v=3e3496ca6d518180bf98000c74142ac8

### 2026-10-11 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Xavi hoy sin vídeo y se autopublica. Sin contenido en Metricool = sin posts.

*Para hoy* 🔔
• Xavi: dom 11/10 — verifica que el vídeo esté listo en Metricool.
• Bandeja: 28 ideas listas para aprobar (Estado=Aprobada, guionizadas esta noche) + 40 sin triar (26 >7 días).
• Creadores de referencia: 9 sin @. Notion → pestaña «✍️ Falta el @» (5 minutos).

*Cómo va lo pendiente*
• ⏳ Jesús Mora — copies en curso, distribución en curso. Mié 14/10 sin programar.
• 🎬 Newmos — grabación esta semana. Dom 18/10 sin programar.
• ⏳ Xavi — 3-4 piezas/semana. Edición y copies listos.

*Recordatorios*
• ⚠️ Análisis de septiembre: 5 clientes pendientes (Newmos y Jesús Mora, más ex-clientes). Brutos de Metricool deberían estar en tu correo. Arrancamos sesión cuando quieras.
• Nota del 31/07: automatizar análisis para la madrugada. En tu lista.

Cuando quieras, aquí estamos 🙌

### 2026-10-12 00:30 · COBERTURA · normal (enviado por: whatsapp)
📅 *Cobertura* — 3 a revisar:

🔴 Jesús Mora: mié 14/10 sin programar
🔴 Newmos: dom 18/10 sin programar · 🎬1
🔴 Xavi: dom 18/10 sin programar · 🎬5

### 2026-10-12 00:30 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tres huecos en la agenda esta semana y la Bandeja de ideas harta. Nada que no se pueda arreglar en una mañana.

*Para hoy* 🔔

• *Programación*: Jesús Mora (mié 14/10), Newmos (dom 18/10) y Xavi (dom 18/10) — ¿qué programa?
• *40 ideas sin triar* en la Bandeja. Las 28 que ya tienen cliente van directas a guiones en cuanto les des OK (Estado=Aprobada).
• *Creadores de Instagram sin @*: 9 referencias esperando el nombre. Tabla en Notion, cambias nombres por @ y listo.

*Cómo va lo pendiente*

• ⏳ Jesús Mora — edición + programación (toca esta semana). Copy del VR de julio ya en borrador.
• 🎬 Newmos — grabación. Dom 18 sigue en blanco.
• ✍️ Xavi — guiones y prep. Tienes OK de estrategia pendiente. Dom 18 sin nada.

*Recordatorios*

• Análisis de septiembre sin arrancar: MidTown, Golossa, Newmos, MSM, Jesús Mora. Cuando quieras arranco al Analista en sesión.

Luego me dices 🙌

### 2026-10-12 00:47 · GUIONES · normal (enviado por: whatsapp)
✍️ Coco guionó anoche 2 idea(s), listas para grabar:

• Jesús Mora: El encargo más raro que nos han pedido
  https://app.notion.com/p/3f6496ca6d518116acacd208abf778b2
• Xavi Colomina: Si la bandeja se te va a la pared de fondo, el pro
  https://app.notion.com/p/3f6496ca6d5181d3b4c3cfa980f7f479

Toca el enlace para abrirla en Notion 📱

### 2026-10-13 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Tenemos 28 ideas en la Bandeja esperando tu OK para guionizar. Y 3 huecos sin cobertura esta semana.

*Para hoy* 🔔
• Bandeja: 28 ideas con cliente asignado esperan Estado=Aprobada para que salgan guionizadas esa noche. Hay 40 ideas más sin triar (llevan +7 días) si quieres ordenar inbox.
• Cobertura — 3 huecos sin programar:
  • Jesús Mora: mié 14 (1 vídeo)
  • Newmos: dom 18 (1 vídeo)
  • Xavi: dom 18 (6 vídeos)

*Cómo va lo pendiente*
• 🔔 Xavi (2026-07) — estrategia lista, edición adelantada. Espera tu OK en estrategia.
• ⏳ Xavi (2026-09) — copies en curso. Distribución hasta el 04/10, dom 18 sin programar.
• ⏳ Jesús Mora — distribución en marcha. Mañana toca programar.
• ⏳ Newmos — es su semana de grabación, dom 18 sin programar.

*Recordatorios*
• 9 creadores de referencia sin @ en Instagram (la mayoría de Jesús Mora) — es mecánico si lo quieres limpio.
• Análisis de septiembre: Newmos y Jesús Mora sin hacer. Tienes nota del 31/07 sobre dejarlos en auto. ¿Retomamos?

Dime qué va primero 🙌

### 2026-10-14 00:31 · DIGEST_CICLO · normal (enviado por: whatsapp)
Bastante cosa hoy, pero todo claro. 3 huecos y la Bandeja espera.

*Para hoy* 🔔
• Jesús Mora: hoy (14/10) sin programar — tú o copy de Coco
• Bandeja: 40 sin triar, 28 con cliente. Solo esperan tu Aprobada para guionizar solos esa noche
• Creadores de referencia: 9 sin @ en IG. Ve a 🎯 Creadores de referencia, pestaña «✍️ Falta el @» y cambia nombres

*Cómo va lo pendiente*
• ⏳ Xavi — guiones y prep, ideas de Oli en Bandeja esperando tu visto bueno
• 🎬 Newmos — grabación en marcha, dom 18/10 sin programar
• ⏳ Jesús Mora — edición en curso, hoy y dom 18/10 sin contenido

*Recordatorios*
• Análisis de septiembre: Newmos y Jesús Mora sin cerrar. Arranca Analista cuando quieras (bruto en el correo)
• Tu nota (31/07): análisis mensuales de madrugada en proyecto nuevo. Pendiente

Tú dices y apretamos 💪
