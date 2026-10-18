# Calendario de publicación — reglas de RM Agency

> Cuándo y cómo se publica. Lo usan el Estratega, Winy y el flujo de distribución.

## ⚠️ Dónde se cambian los días

**Los datos viven en `config/publicacion.json`. Es la fuente única.**

Este fichero **explica**, no repite. Si hay que cambiar un día, una pausa o una excepción,
se toca **solo el JSON** y todo el sistema se entera: el chequeo de cobertura
(`infra/metricool/chequeo_cobertura.py`) y el repartidor de slots
(`infra/programacion/calendario.py`) lo leen de ahí.

> Antes esto vivía duplicado aquí y en el código, y se desincronizaba. Ya no: **no vuelvas a
> escribir días concretos en este fichero.**

## Reglas generales (todos los clientes)

- **Hora de publicación: siempre 15:00.**
- **Reels duplicados**: cada pieza de vídeo vertical se publica en **Instagram (Reel)** y en
  **TikTok** — el mismo contenido en las dos redes.
- **Historias**: en testeo, **NO se publican/programan aún**.

## Los tres conceptos del JSON

| Concepto | Qué es | Ejemplo |
|---|---|---|
| **`dias`** | El ritmo normal del cliente. `_default` vale para quien no tenga entrada propia. | Golossa: miércoles y domingo |
| **`pausas`** | El cliente **no publica** en ese rango. No se le consulta ni se avisa de huecos. `hasta: null` = sin fecha de vuelta. | Midtown, todo agosto |
| **`excepciones`** | El cliente publica, pero con **otros días** durante un rango. Al acabar vuelve solo a su ritmo normal. | Jesús Mora, agosto: solo domingos |

Las pausas y excepciones **caducan solas**. No hay que acordarse de deshacerlas: el 1 de
septiembre, Midtown y Jesús Mora vuelven a su ritmo normal sin tocar nada.

## Estado a 09/09/2026

| Cliente | Ahora |
|---|---|
| **Golossa** | ❌ Fuera de roster, sin fecha de vuelta |
| **MSM** | ❌ Fuera de roster, sin fecha de vuelta |
| **Jesús Mora** | Miércoles y domingo (vuelve a su ritmo el 22/09/2026; hasta entonces, solo domingos) |
| **Midtown** | ⏸ En pausa indefinida |
| **Newmos** | ✅ Activo — domingos a las 15:00 |
| **Xavi** | ✅ Activo — martes, jueves y domingo a las 15:00 |

> 🔔 **Pendiente**: cuando se concreten los días de Xavi, quitarle la pausa y añadir su
> entrada en `dias` del JSON.
