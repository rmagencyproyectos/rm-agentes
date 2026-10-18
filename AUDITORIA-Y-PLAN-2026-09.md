# Auditoría del sistema + borrador del plan a 6 meses

> **Fecha**: lunes 21/09/2026. **Horizonte del plan**: oct 2026 → mar 2027.
> **Qué se ha mirado**: los 8 agentes, los 8 automatismos (launchd), los logs de las
> últimas 8 semanas, las hipótesis y métricas en disco, el `RM Operation System`
> (`proyectos/qu/`), precios, finanzas y todas las carpetas de `~/rmagency`.
> **Qué NO se ha tocado**: nada. No se ha movido, borrado ni cambiado ningún archivo.
> El editor de vídeo queda fuera a propósito (va al final).

> **Actualización 21/09 (respuestas de Gerard)**: objetivo **8.000 €/mes**. Facturación actual
> **1.150 €/mes** = Jesús Mora (650) + Newmos (500). **Ya no son clientes**: MSM, Golossa,
> Midtown, Algoritmo. **Xavi** es una sociedad al 50 % de beneficios: hoy 0 €, proyecto a largo
> plazo. **Andrea y Jaume trabajarán dentro de Notion.** Las secciones 6-8 están reescritas con
> estos datos; las secciones 1-5 describen el sistema tal como estaba.

---

## 1. El diagnóstico en una frase

**El diseño del sistema es bueno y ya contempla casi todo el bucle que quieres; lo que
falla es la fontanería y las puertas humanas.** Los automatismos corren cada noche sin
errores y no producen nada: no les falta inteligencia, les falta que les llegue trabajo
y datos frescos.

Tres pruebas:

| Síntoma | Dato |
|---|---|
| La fábrica de guiones está parada | Último guion: **31/08** (1 pieza). Desde entonces, 21 noches seguidas de "Nada que guionizar". La Bandeja pasó de 14 ideas atascadas (11/08) a **28** (16 con cliente puesto, a un clic). |
| El bucle de aprendizaje nunca se ha cerrado | **40 apuestas escritas** en `hipotesis.json` (Golossa 13, Jesús Mora 13+8, Xavi 5, Midtown 1). **0 enlazadas a su post publicado, 0 con resultado.** `termometro.py --revisar` → "No hay tandas que cerrar". |
| Las métricas están congeladas | `memoria/metricas/*` y `_posts/*` son del **11/08**. Nadie ejecuta `fetch_metricool.py` de forma automática. El Analista no ha hecho **agosto** de ningún cliente. El registro de aprendizajes no tiene una entrada nueva desde el **11/08**. |

Winy lleva semanas avisando de lo mismo (Bandeja, notas vencidas desde el 05/08) y los
avisos ya no mueven nada. Es exactamente la fatiga de alertas que el plan de agosto quería
evitar.

---

## 2. Estado agente por agente

Leyenda: 🟢 corre y produce · 🟡 corre pero no produce / a medias · 🔴 no corre · ⚪ solo documento

| Agente | Cómo se activa | Estado real | Qué hace bien | Qué le falta |
|---|---|---|---|---|
| **Winy** (coordinadora) | Cron 00:30 + WhatsApp 24/7 | 🟢 | Check-in diario fiable, cobertura real, captura por WhatsApp (texto y audio), memoria de 30 días, coste bajo (~0,05-0,09 $ el check-in) | Repite el mismo aviso durante semanas sin escalar ni caducar. Guardar un link de IG cuesta **0,12-0,34 $** (va a Sonnet) y deja "referencia genérica" sin contenido, que acaba en la Bandeja como idea vacía. No distingue lo urgente de lo que ya se ha avisado 20 veces. |
| **Coco** (guiones + copy) | Cron 00:45 | 🟡 **parada** | Guion de tres capas (espina + tipo + plantilla), copy en la misma pasada, escribe la hipótesis, tope de coste, no inventa datos | No le llega nada: depende de que alguien apruebe en la Bandeja. Solo guioniza ideas sueltas; no trabaja por **serie** ni por **trimestre**. `copy-brief.md` solo existe para algunos clientes. |
| **Oli** (estratega) | A mano (`olivia.sh`) | 🟡 | Contrato de transparencia excelente (evidencia, descartes, riesgos, datos que faltan). Hizo la tanda de 8 de Jesús Mora. | Solo planifica **una tanda mensual**. No existe el entregable que pides: **estrategia de 3 meses** (análisis de negocio → objetivos → pilares → series → formatos → calendario de rodaje). Sus datos de entrada están congelados desde el 11/08. |
| **Analista** (cierre de mes) | A mano (`analista.sh`) + PDF de Metricool por email | 🔴 desde el 02/08 | Deck de 14 páginas en catalán en Canva, con lente de negocio y clasificación por plantilla | Agosto sin hacer. Depende de descargar PDFs a mano y de Canva: es lo más caro de operar. No escribe aprendizajes en el registro. No compara entre clientes. |
| **Termómetro** (medir hipótesis) | Dentro de `estado.py` | 🔴 en la práctica | La idea es la correcta: mediana del cliente, IG+TikTok sumados, 14 días de espera | Tres cortes: (1) las métricas no se refrescan, (2) la hipótesis no guarda el ID del post publicado, así que no hay con qué cruzarla, (3) nadie ejecuta `--cerrar`. |
| **Clasificación** | Cron 00:45 | 🟢 pero con poca cobertura | Etiqueta cada pieza con plantilla, palanca y metodología | Solo Xavi está bien clasificado (52/55). Golossa 1/15, Jesús 2/9, Midtown 0/8, MSM 0/7. Todo lo anterior al 13/08 no se puede reconstruir. |
| **Autoprogramar** | Cron 00:45 | 🟡 **nunca se dispara** | Hueco → copy → borrador en Metricool → Notion → aviso | Se activa con Producción=Editado + vídeo con URL en Notion. **El equipo no marca eso en Notion**, así que nunca hay nada. Xavi se programó a mano en sesiones. |
| **Cobertura** | Cron 00:30 | 🟢 | Huecos reales de publicación con pausas y excepciones | Nada importante. |
| **Iris** (QA) | — | ⚪ stand-by | Checklist bien definida (bloqueante vs aviso) | No existe en código. **Riesgo real hoy**: Xavi autopublica sin revisión humana. |
| **Nova** (mantenimiento) | A petición por Winy | 🟢 como convención | Propone y espera OK, deja registro | Nada importante. |
| **Editor** | Skills interactivas | 🟡 | Pipeline de Xavi probado | Solo un estilo (Xavi). **Aparcado hasta el final, como pediste.** |
| **Comercial** | — | ❌ **no existe** | — | No hay agente, CRM, base de leads, secuencias ni métricas de embudo. Solo hay dos Excels de prospección sueltos (náutica y academias). |
| **Finanzas / MRR** | — | ❌ **no existe** | — | Los cobros se controlan con pizarra física + banco. No hay una cifra de MRR actual fiable. |

Otras piezas:

- **Project Pocket** (calendario, Vercel + local): funciona y sincroniza Notion ↔ Metricool. **Duda**: ¿lo usáis de verdad a diario? Si no, está sumando complejidad.
- **`/generate` + Open-Generative-AI**: montado; solo Muapi está implementado, el resto de proveedores son stubs. 1,3 GB. No hay evidencia de uso reciente.
- **Crons que existen pero no están cargados**: `caffeinate` y `limpiar-copies`. Hay que decidir si se cargan o se borran.

---

## 3. Qué falta para el bucle que quieres

Tu bucle, pieza por pieza, contra lo que existe:

| Paso | Existe | Estado | Qué hay que hacer |
|---|---|---|---|
| Estrategia (3 meses) | Oli (mensual) | 🟡 | Nuevo entregable trimestral + plantilla de estrategia |
| Ideas | Bandeja + Winy | 🟡 atascado | Nueva regla de entrada (ver §5, P0-3) |
| Series / formatos | Plantillas de guion (catálogo) | 🟢 base | Añadir la **serie** como unidad (hoy solo existen piezas sueltas) |
| Guiones | Coco | 🟢 código / 🔴 flujo | Guionizar por lote trimestral, no pieza a pieza |
| Organizar rodajes | — | ❌ | **Agente de rodaje**: agrupa guiones por persona, localización y vestuario → orden de rodaje + hoja de llamada |
| Grabación | Humano | — | — |
| Edición | Editor + freelance | 🟡 | Al final |
| Revisar antes de publicar | Iris | ⚪ | Encender en versión mínima (copy + datos + marca) |
| Publicación | Programar / autoprogramar | 🟢 / 🟡 | Decidir si Notion manda de verdad o se simplifica |
| Datos | `fetch_metricool` | 🔴 congelado | Cron semanal |
| Análisis IA | Analista + termómetro | 🔴 | Análisis automático en Markdown; Canva solo para lo que ve el cliente |
| Aprendizajes | `registro.md` | 🔴 desde el 11/08 | Que el Analista y el termómetro escriban aquí solos |
| Nuevas ideas / nueva estrategia | Oli lee aprendizajes | 🟡 | Se arregla solo si se arregla lo anterior |

**Conclusión**: no hace falta inventar agentes nuevos para el bucle de contenido, salvo el
**agente de rodaje** y la **estrategia trimestral**. Hay que conectar lo que existe. Lo que
sí falta desde cero es **todo el lado comercial y financiero**.

---

## 4. Desorden de archivos

### Hay cinco "cerebros" que se pisan

1. `AGENTES RM/` — el sistema vivo (agentes, memoria, config, infra).
2. `proyectos/qu/outputs/RM Operation System/` — la documentación de negocio (precios,
   finanzas, ventas, procesos). Hecha con Codex en julio: **dice que los copies se hacen con
   ChatGPT y que no hay automatización**, así que está desfasada. Y se llama `qu`.
3. `proyectos/fabrica-contenido/` — perfiles de marca para edición (Xavi, MSM).
4. Fábricas por cliente en el disco externo (`FABRICA VIDEOS XAVI`).
5. Notion (bases de contenido, Bandeja, accesos).

Además hay copias muertas en `~/Documents/Claude/AGENTES RM` y `~/Documents/Codex/…` que ya
están documentadas como trampas.

### Inventario de `~/rmagency`

| Qué | Tamaño | Veredicto |
|---|---|---|
| `AGENTES RM/` | — | **Se queda con este nombre** (los crons, el servidor y las fábricas usan la ruta absoluta; renombrarlo lo rompe todo) |
| `proyectos/qu/…/RM Operation System` | pequeño | Subir a nivel raíz como `empresa/` y actualizar `config/rutas.md` |
| `proyectos/Calendario Edición` | 2,5 MB, git | Herramienta. Se queda |
| `proyectos/remotion-video` | **8,1 GB** (5,7 GB de vídeo en `public/`) y 53 cambios sin commitear | Sacar el vídeo al disco. Editor → al final |
| `proyectos/golossa-montajes` | 563 MB, sin git | Archivar en disco |
| `proyectos/fabrica-contenido` | 316 KB, git | Fusionar con las fábricas por cliente o archivar |
| `proyectos/Analisis mensual` | 277 MB de PDFs | Runbook se queda; los PDFs antiguos al disco |
| `proyectos/Compatibilidad laboral Kelly Isaiah` | 449 MB | Otro proyecto, no es RM → archivo |
| `proyectos/yoruba-carousel-muestra` + `.zip` | 19 MB | Muestra comercial → `comercial/muestras/` o archivo |
| `proyectos/Cowork`, `proyectos/examples` | vacías | Borrar |
| `Open-Generative-AI/` | 1,3 GB | Herramienta; decidir si se usa |
| `outputs/prospeccion_nautica`, `academias_PEE_PRV_instagram.xlsx` (raíz) | — | → `comercial/leads/` |
| `outputs/golossa_badalona` | — | Entregable de cliente → carpeta del cliente |
| `AGENTES RM/output/golossa` | — | Mismo caso (hay `outputs/` en tres sitios) |
| `AGENTES RM/infra/.env.bak.*` (6) + `.env.winston` | — | **Seis copias de los secretos.** Dejar una sola copia de seguridad fuera del vault |

### Estructura propuesta (a aplicar tras tu OK, con checklist de rutas)

```
~/rmagency/
├── 00 Inicio.md            ← mapa único (sustituye a "RM Agency — Inicio.md")
├── AGENTES RM/             ← el sistema (NO se renombra)
├── empresa/                ← antes proyectos/qu/…/RM Operation System, puesto al día
│   ├── oferta/             ← servicios, precios, contrato, condiciones
│   ├── finanzas/           ← MRR, costes, margen
│   └── procesos/
├── comercial/              ← NUEVO: leads, CRM (o enlace a Notion), propuestas, muestras, casos
├── herramientas/           ← Calendario Edición, remotion-video, Open-Generative-AI
├── notas/
└── (todo lo demás → disco externo, "RM Agency — Archivo/")
```

Antes de mover nada hay que buscar rutas absolutas en: plists de launchd, `config/rutas.md`,
`server.js` del calendario, los symlinks de `~/.claude/skills/`, los `CLAUDE.md` de las
fábricas y el segundo Mac (`gerardrm`).

---

## 5. Por dónde tirar: agentes, por prioridad

### P0 — esta semana (horas, no días)

1. **Métricas vivas**: cron semanal de `fetch_metricool.py` (domingo de madrugada). Sin esto,
   todo lo demás razona sobre datos de agosto. Xavi aparece "sin datos" porque la última
   descarga es anterior a su arranque del 01/09.
2. **Cerrar el bucle de hipótesis**: guardar en cada hipótesis el ID de la página de Notion. El
   sync Metricool → Notion ya escribe el "Metricool ID", así que el termómetro puede cruzar
   hipótesis → Notion → post → vistas. Después, `--cerrar` automático cada semana para las
   piezas con más de 14 días, y que escriba el resultado en `registro.md`.
3. **Desatascar la Bandeja, y que no vuelva a pasar**:
   - Hoy: 20 minutos para triar las 28 (aprobar 16, archivar el resto).
   - Regla nueva: **un link sin una frase no es una idea**. Si Winy recibe un link solo, lo
     guarda como *Referencia* (otra vista, no la Bandeja) y pregunta en una línea "¿qué te
     gusta de este?". La respuesta lo convierte en idea.
   - Guardar un link no debería pasar por Sonnet (hoy 0,12-0,34 $ cada uno): ruta barata.
4. **Higiene de avisos**: un aviso que se repite 7 días seguidos pasa a un resumen semanal
   y deja de salir cada noche. Cerrar las 4 notas vencidas desde agosto. Cerrar los ciclos
   de julio que siguen "en curso" (Xavi y Jesús Mora).
5. **Iris mínima para Xavi**: como autopublica, una revisión automática del copy (datos
   inventados, CTAs de venta prohibidos desde el 07/09, ortografía) antes de crear el post
   en firme.

### P1 — octubre

6. **Oli trimestral**: entregable nuevo `ciclos/2026-Q4/<cliente>/estrategia.md` con análisis
   del negocio, objetivo de negocio medible, 3-4 pilares, 2-3 **series** con formato fijo,
   calendario de 3 meses y la tanda de hipótesis. Es la base del servicio nuevo.
7. **Agente de rodaje** (nuevo): de los guiones aprobados del trimestre saca el plan de
   jornadas (agrupado por persona, localización, vestuario y luz), el orden de rodaje, el
   material y la hoja de llamada para el cliente. Objetivo: 1-2 jornadas por cliente y trimestre.
8. **Analista automático en dos capas**: (a) análisis interno en Markdown sacado de la API de
   Metricool, sin Canva y sin PDF, que corre solo el día 2 de cada mes y alimenta el registro;
   (b) deck para el cliente solo cuando toca (trimestral), a partir de (a).
9. **Decidir qué pasa con Notion como fuente de verdad.** Si el equipo y el freelance no van a
   marcar estados en Notion, autoprogramar y el calendario no tendrán nunca datos. O se
   adopta con una regla simple o se simplifica el flujo.

### P2 — noviembre y diciembre

10. **Agente comercial** (nuevo): búsqueda de prospectos por sector y zona → enriquecimiento
    (web, redes, seguidores, frecuencia de publicación, contacto) → puntuación de encaje →
    primer mensaje personalizado (borrador, lo envía una persona) → seguimiento. CRM en Notion.
11. **Informe de cliente con métrica de negocio** (la Pieza D de agosto, que sigue pendiente):
    un número por cliente que no sean visitas (leads al DM, reservas, pedidos, llamadas).
12. **Patrones entre clientes**: `termometro.py --plantillas` + clasificación → informe
    trimestral de qué ganchos, formatos, duraciones y plantillas funcionan en toda la cartera.
    Esto también es **material de venta** (casos, datos propios).

### P3 — al final

13. Editor de vídeo (estilos por cliente en Remotion, pre-corte para el freelance).

---

## 6. El objetivo con los datos reales

**De 1.150 € a 8.000 € = +6.850 €/mes en 6 meses.** Casi todo tiene que venir de clientes
nuevos. Esto cambia el orden de prioridades: **la captación pasa de P2 a P0.** El sistema de
contenido ya está sobredimensionado para 2 clientes; lo que falta es tener a quién servir.

### Cuentas
| Escenario | Base | Falta | Clientes nuevos a 1.300 € |
|---|---:|---:|---:|
| Sin tocar precios | 1.150 € | 6.850 € | **5-6** |
| Jesús Mora y Newmos a tarifa oficial | 2.080 € | 5.920 € | **4-5** |

**Se cobra a mes vencido**: para facturar 8.000 € en marzo, los clientes tienen que estar
trabajando en febrero, es decir, **cerrados como tarde a mediados de febrero**. El plazo real de
venta son 4,5 meses, no 6.

### Precios: qué reajustar (solo quedan dos casos)
- **Jesús Mora**: paga 650 € (pack de 4) y recibe 8 vídeos. La tarifa de 8 es 1.170 €.
  Opciones al pasarlo a trimestral: (a) 8 vídeos a 1.170 €, o (b) volver a 4 vídeos a 650 €.
  **Recomendación: (b) si no acepta (a).** Con 1.150 € de base no conviene arriesgar a un cliente,
  pero regalar 4 vídeos al mes quita justo el tiempo que ahora hace falta para vender.
- **Newmos**: 500 € por 4 vídeos + 4 carruseles (tarifa 910 €). Edición lenta y poca
  disponibilidad. **Recomendación: no subir precio todavía; bajar la complejidad** (formatos
  repetibles) para que deje margen.
- **Lo importante es el precio del servicio nuevo.** La estrategia de 3 meses con rodajes
  concentrados, informe y optimización vale más que los packs antiguos. Propuesta de partida:
  **1.300-1.600 €/mes con compromiso de 3 meses**, y una puerta de entrada más barata
  (consultoría o auditoría) para quien no está listo.

### Alerta de caja
Los costes fijos documentados son **1.154 €/mes** (herramientas, autónomos, gestoría y
editores), frente a 1.150 € de ingresos. **Hoy la empresa no cubre costes.** Hay que revisar si los
550 € de editores siguen teniendo sentido con 2 clientes y saber cuántos meses de colchón hay.

### Xavi
Cuenta como activo estratégico y caso de éxito, **no como ingreso del plan**. Hay que ponerle
un tope de horas semanales para que no se coma el tiempo de venta.

### Embudo necesario (hipótesis que hay que validar)
5 cierres con un 25-30 % sobre propuesta → ~18 propuestas → ~35 reuniones → **~500 contactos
personalizados** en 20 semanas = **25 contactos a la semana**. Sin un agente comercial que prepare
las listas y los mensajes, ese volumen no es sostenible a mano.

### Cuadro de mando (cada lunes)
| Área | Métrica | Meta |
|---|---|---|
| Negocio | MRR contratado | oct 2.500 · nov 4.000 · dic 5.000 · ene 6.500 · **feb 8.000** |
| | Ticket medio clientes nuevos | ≥ 1.300 € |
| | Contratos de 3 meses firmados | 100 % de los nuevos |
| Comercial | Contactos / respuestas / reuniones / propuestas / cierres | 25 / — / 2 / 1 / — a la semana |
| Producción | Colchón programado por cliente | ≥ 21 días |
| Sistema | Hipótesis cerradas con dato | ≥ 80 % |
| | Avisos repetidos más de 7 días | 0 |

---

## 7. Roadmap (versión 2)

### Mes 0 · 22/09 → 04/10 — Limpiar y preparar la venta
- **Sacar del sistema a los ex-clientes** (Golossa, Midtown, MSM, Algoritmo): config, crons,
  cobertura, reloj y bases activas de Notion. Archivar sus ideas de la Bandeja. Así Winy deja de
  avisar de clientes que ya no existen.
- P0 técnico solo para Jesús Mora, Newmos y Xavi: métricas vivas, cerrar el bucle de hipótesis e
  Iris para Xavi.
- **Regla de Notion para Andrea y Jaume** (una página): qué estado marca cada uno y cuándo.
  Con eso, autoprogramar y el calendario empiezan a tener datos.
- Decidir la oferta trimestral y su precio. Definir el cliente ideal (sector y zona).
- Revisar la caja: costes fijos frente a 1.150 € y meses de colchón.

### Mes 1 · octubre — Máquina comercial en marcha
- Material de venta: oferta de una página, 2-3 casos con datos (**Golossa sigue sirviendo como
  caso**: 2,4 M de alcance en julio y aperturas; Xavi como caso de marca personal), propuesta tipo.
- **Agente comercial v1**: prospectos por sector y zona → enriquecimiento → puntuación → borrador de
  mensaje (lo envía una persona) → CRM en Notion. Objetivo: 200 prospectos cargados.
- 25 contactos a la semana desde la S2. Probar 2 canales.
- Proponer el paso a trimestral a Jesús Mora y Newmos (precios de §6).
- **Hito**: 6-8 reuniones, 1 cierre. MRR contratado 2.500 €.

### Mes 2 · noviembre — Vender y entregar el método
- 25-30 contactos a la semana; recalcular el embudo con las tasas reales de octubre.
- Oli trimestral + agente de rodaje, estrenados con el primer cliente nuevo.
- Marca propia RM: 1 pieza a la semana (casos y aprendizajes). Es un canal de captación.
- **Hito**: 2 cierres acumulados más. MRR contratado 4.000 €.

### Mes 3 · diciembre — Llenar enero
- Diciembre cierra poco: se agendan reuniones para enero.
- Rodajes concentrados del primer trimestre de los clientes nuevos.
- Analista automático + informe de cliente con métrica de negocio.
- **Hito**: MRR contratado 5.000 € y ≥ 8 reuniones agendadas para enero.

### Mes 4 · enero — Pico comercial
- Las empresas planifican el año: es el mejor mes para vender.
- **Hito**: MRR contratado 6.500 €.

### Mes 5 · febrero — Último cierre y delegar
- Cierres hasta mediados de mes (para facturar en marzo).
- Manual del freelance y editor de vídeo (aquí entra el agente de edición).
- **Hito**: MRR contratado 8.000 €.

### Mes 6 · marzo — Facturar 8.000 € y revisar
- Primera factura de 8.000 €. Revisión: qué canal funciona, margen real, capacidad.
- Plan de los 6 meses siguientes.

---

## 8. Decisiones pendientes
1. Precio y contenido exacto de la oferta trimestral.
2. Cliente ideal: sector(es) y zona para prospectar.
3. Jesús Mora: ¿8 vídeos a 1.170 € o 4 a 650 €?
4. Caja: ¿cuántos meses aguantáis con 1.150 €? ¿Se mantienen los 550 € de editores?
5. Horas semanales máximas para Xavi.

---

## 9. Actualización 21/09 (tarde)

- **Limpieza hecha**: ex-clientes fuera del sistema (detalle y cómo revertir en `memoria/cambios-sistema.md`).
- **Zona**: Lleida. **Sector principal**: inmobiliarias, con un producto cerrado: tour del piso +
  reforma con IA por habitaciones (del estado actual a un "así podría quedar" y vuelta al tour).
  Sin estrategia ni planificación: grabar, editar, entregar, cobrar. Candidatos parecidos:
  compraventa de coches y otros sectores de "enseñar algo único".
- **Segunda línea**: proyectos más creativos con la estrategia de 3 meses (sector por definir).
- **Caja**: aguantáis bastantes meses. Sin editores, los costes documentados son 604 €/mes
  (pendiente de que Gerard confirme las cifras reales).
