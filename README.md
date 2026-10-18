# AGENTES RM — Sistema de agentes de IA para RM Agency

Hub que **orquesta y unifica** la operación de RM Agency en 6 agentes que trabajan por
**ciclo mensual** (grabación → edición en bloque → distribución → análisis de cierre) y
dejan a Gerard **solo notificaciones**: cómo va todo + problemas que debe resolver él.

> Principio rector (heredado de `fabrica-contenido`): **separar el *cómo* (skills/SOP
> reutilizables) del *qué* de cada cliente (datos = fichas)**. El sistema no parte de
> cero: referencia lo que ya existe (ver [`config/rutas.md`](config/rutas.md)) y no lo
> duplica.

## Mapa

| Carpeta | Qué es |
|---|---|
| `agentes/` | SOP + personalidad de cada agente (capas 1 y 4 del patrón de 4 capas). |
| `memoria/clientes/` | **Capa 1 de memoria**: ficha viva por cliente (fuente de verdad). |
| `memoria/aprendizajes/` | **Capa 2 de memoria**: registro append-only de aprendizajes/correcciones. |
| `ciclos/` | El "bus": estado (`manifest.json`) y output por ciclo mensual y cliente. |
| `config/` | Rutas a repos externos, horarios (cron) y plantillas/reglas de avisos. |
| `infra/` | Self-hosting en la Mac: Evolution API (WhatsApp), notificador, energía/arranque. |
| `INBOX-GERARD.md` | Bandeja única legible; Winston vuelca aquí el digest de cada ciclo. |

## Los 6 agentes

- **Winston / Winy** (N1) — Coordinador de Operaciones. Recopila, agrupa por ciclo, notifica.
- **QA** (N1) — Control de Calidad. Última barrera antes de que algo llegue a Gerard.
- **Estratega** (N2) — Decide qué grabar/publicar según métricas y aprendizajes.
- **Editor de Vídeo** (N3) — Convierte material grabado en piezas publicables.
- **Copywriter / Creativo** (N3) — Copy + hashtags + CTA por pieza, en el tono del cliente.
- **Analista** (N3) — Análisis mensual de cierre: bruto de Metricool → deck en Canva por cliente.

## Autonomía: "interno sí, salida no"

Los agentes preparan y deciden lo **interno**. Todo lo que **sale** cruza una puerta 🚪
que aprueba Gerard:
- 🚪 **Gate 1** — shot list del Estratega antes/durante la grabación.
- 🚪 **Gate 2** — envío del lote al WhatsApp del cliente.
- 🚪 **Gate 3** — programación en Metricool.
- 🚪 **Gate 4** — deck de análisis del Analista: queda listo en Canva para el **check final de
  Gerard**; el PDF y el envío al cliente salen tras su OK.

## Estado

- **Fase 0** (en curso): hub creado, fichas de cliente unificadas, config base.
- Ver el plan completo: `~/.claude/plans/quiero-que-me-ayudes-memoized-koala.md`.
- Roster v1 (con ficha): Golossa, Midtown, Jesús Mora, MSM, Newmos, Xavi Colomina.
  Fuera de v1 por ahora (sin ficha completa): Nymus, Margarita, Tita 354, Arquitek.
