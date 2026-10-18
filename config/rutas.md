# Rutas canónicas (repos referenciados, NO duplicados)

El hub apunta a lo que ya existe. Si mueves alguno de estos repos, actualiza aquí.

## Ubicación del sistema (hub) y vault de Obsidian
- **Hub del sistema de agentes**: `/Users/gerardruizmiro/rmagency/AGENTES RM`
  (se movió aquí desde `~/Documents/Claude/` porque macOS no deja que los procesos
  automáticos de launchd lean `~/Documents` — TCC. Fuera de Documents corre solo sin permisos.)
- **Vault de Obsidian de Gerard**: `/Users/gerardruizmiro/rmagency`
  Es la fuente central de información. Lo que Gerard escriba aquí lo leen TODOS los agentes
  (incluida la Winy automática). Notas sueltas de Gerard → `notas/` (los agentes las ojean).
- ✅ **Desde el 13/08/2026 los repos de negocio también viven dentro de `~/rmagency/proyectos/`.**
  Antes estaban en `~/Documents` (protegido por TCC): los agentes interactivos los leían, pero
  los automáticos de launchd **no**. Al migrarlos, esa distinción desaparece — cualquier
  proceso puede leerlos. Los pesados (Editor, Análisis) se siguen corriendo en sesión
  interactiva, pero ya por tamaño de la tarea, no por permisos.

## Repos de negocio

| Alias | Ruta | Qué contiene |
|---|---|---|
| `OPERATION` | `/Users/gerardruizmiro/rmagency/proyectos/qu/outputs/RM Operation System` | Cerebro documental: `procesos/`, `clientes/`, `ventas/`, `administracion/`, `ideas/banco-de-ideas.md`. |
| `FABRICA` | `/Users/gerardruizmiro/rmagency/proyectos/fabrica-contenido` | Perfiles semilla de cliente (`clientes/<slug>/perfil.md` + `marca.json`) y tipos de vídeo. |
| `ANALISIS` | `/Users/gerardruizmiro/rmagency/proyectos/Analisis mensual` | Runbook Metricool→Canva→PDF (`CLAUDE.md`) + `registro-analisis.json`. **Dueño: el Analista** (`agentes/analista.md`). |
| `REMOTION` | `/Users/gerardruizmiro/rmagency/proyectos/remotion-video` | Motor de vídeo + skills (`transcripcion-momentos`, `edicion-clips`, `edicion-multicam`). |
| `CALENDARIO` | `/Users/gerardruizmiro/rmagency/proyectos/Calendario Edición` | Prototipo del flujo edición→entrega→publicación (regla entrega = publicación − 72h). |

> ⚠️ Quedan copias muertas de `OPERATION` en `~/Documents/Codex/2026-07-07/…`. **No son el
> sistema.** Si editas una por error, el hub no se entera. Misma trampa que la copia muerta
> del propio hub en `~/Documents/Claude/AGENTES RM`.

## Procesos clave (dentro de OPERATION/procesos/)

| Agente | SOP de negocio de referencia |
|---|---|
| Estratega | `01-estrategia-e-ideas.md`, `00-ciclo-mensual-real.md`, `ideas/banco-de-ideas.md` |
| Editor | `03-edicion.md`, `08-editor-freelance.md`, `07-organizacion-archivos.md` |
| Copywriter | `04-copies.md` (incluye prompt base de MSM) |
| QA | `10-incidencias.md`, reglas anti-overflow de `ANALISIS/CLAUDE.md` |
| Analista | `05-analisis.md`, `ANALISIS/CLAUDE.md` (dueño del análisis de cierre) |
| Winston / cierre | `09-calendario-operativo.md` (consolida el digest de cierre; no produce el análisis) |

## Material de cliente (discos)

- Xavi Colomina: `/Volumes/DD 2 TB WORK/Xavi Colomina/Videos/` (+ `EXPORTS/`).
- MSM: `/Volumes/DD 2 TB WORK/MSM/Story CTA/`.
- Resto de clientes: **TBD** (documentar ruta de fuentes por cliente — ver §7 del plan).

## Panel "Qué vídeos hacer" (02/10/2026)
- **URL (Artifact privado)**: https://claude.ai/artifact/G3TauovZbxu6BoWtzDd8bE
- Datos: `infra/analisis/panel_datos.py` (cada noche en `notion/noche.sh`) → `memoria/analisis/`
  + `infra/analisis/web/` (panel.html ligera + datos.json + fuentes).
- **Se publica sola cada mañana (~05:00)**: tarea programada de la app de Claude
  «Panel: publicar «Qué vídeos hacer»» (`~/.claude/scheduled-tasks/panel-que-videos-hacer-publicar/`).
  Solo sube `datos.json`; corre si la app de Claude está abierta (si no, al abrirla).
