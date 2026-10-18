# Horarios / loops (cron)

Los agentes se disparan por tareas programadas del entorno Claude Code. Claude Code no
tiene "eventos" nativos: los "disparos por evento" son **polls** que inspeccionan el
estado del `manifest.json` de cada ciclo/cliente y despachan lo que esté `pendiente`.

| Agente | Cuándo | Qué hace al dispararse |
|---|---|---|
| **Estratega** | Mensual, ~N días antes de la ventana de grabación de cada cliente | Relee el análisis de cierre anterior + aprendizajes → escribe `estrategia/shotlist.md`. 🚪 Gate 1. |
| **Winston** | Check-in **diario** (00:30) + **cierre de mes** + inmediato ante fallo | Lee todos los `manifest.json`, agrupa, despacha pendientes, escribe el digest en `INBOX-GERARD.md` y notifica. |
| **Editor** | Poll (vía check-in de Winston) cuando `grabacion.estado=hecha` | Procesa material con las skills → deja punteros en `edicion/`. |
| **Copywriter** | Poll cuando hay pieza editada | Escribe copy por pieza en `copies/`. |
| **QA** | Poll cuando Editor/Copywriter marcan piezas "listas" + barrido pre-Gate 2 | Valida y marca `qa.estado`. |
| **Analista** | Aviso en el check-in diario (headless) + arranque manual | Winy avisa de los análisis del mes que faltan (`estado.py` → `leer_analisis_pendiente`, cruza el registro; días 1-20). Gerard arranca la sesión interactiva con `infra/analista/analista.sh`; corre `ANALISIS/CLAUDE.md` y deja el deck de Canva listo para su check. Tarea pesada → **sesión interactiva**, no launchd. |

## Regla horaria — TODO lo automático corre de MADRUGADA
Convención fija de Gerard: cualquier tarea automática se ejecuta **a partir de las 00:00**,
nunca de día, para no gastar tokens de Claude cuando él lo está usando por la mañana.
- **Winston (check-in DIARIO)**: **todos los días 00:30**. LaunchAgent
  `com.rmagency.winston-checkin` (ver `infra/launchd/`). Corre `infra/winston/winston-checkin.sh`
  (Claude headless con `CLAUDE_CODE_OAUTH_TOKEN` de `infra/.env.winston`).
- **Limpieza mensual (Nova)**: **día 1 de cada mes 03:00**. LaunchAgent
  `com.rmagency.limpieza-mensual` → `infra/mantenimiento/limpieza.sh` (bash puro, sin Claude).
  Vacía logs volátiles + ids anti-bucle, poda la memoria a 30 días y borra basura
  (.DS_Store, temporales). No toca datos de negocio. Deja constancia en `memoria/cambios-sistema.md`.
- **Winy conversacional (WhatsApp)**: LaunchAgent `com.rmagency.responder` (servidor siempre vivo).
- **Estratega (mensual)** y cualquier cron futuro: programar también en franja de madrugada.

## Parámetros a decidir (TBD)
- Valor de **N** (días de antelación del Estratega) por cliente → y su hora exacta de madrugada.
- Día de disparo del cierre de mes (depende de cuándo llegan los brutos de Metricool).

## Implementación
- Se registran con las tareas programadas del entorno (launchd/cron). La Mac debe estar despierta
  (ver `infra/` §11 del plan): auto-arranque + anti-suspensión.
- Cambiar día/hora de Winston: editar `Weekday`/`Hour`/`Minute` en el plist y recargar
  (`launchctl unload && launchctl load`).
