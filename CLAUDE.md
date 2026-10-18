# AGENTES RM — mapa del sistema

Hub del sistema de agentes de **RM Agency** (agencia de contenido). Gerard es el jefe; los
agentes le llevan la operación mensual de cada cliente.

**Este archivo es el mapa: no hace falta explorar el hub para orientarse.** Lee directamente
el archivo que necesites.

## Reglas duras

1. **No leas los `.json` de `memoria/metricas/`** — son datos crudos. Para hablar de métricas
   usa el `.md` del mismo cliente, que es el resumen legible.
2. **No hagas barridos del hub** ("a ver qué hay"). El mapa está aquí; ve directo al archivo.
3. **Gates que no se cruzan nunca**: no se envía nada a clientes ni se programa en Metricool.
   Eso lo aprieta Gerard. Se le deja listo y se le avisa. **Cuando Gerard dice "programa" en la
   conversación, se programa DEL TODO** (borrador + `infra/metricool/firmar.py`, sale solo, sin
   preguntar "¿lo firmo?") — regla suya del 09/10/2026. Nunca por iniciativa propia ni por cron.
   > **Avisos (regla de Gerard, 22/09/2026):** el email/WhatsApp es para lo que ocurre **solo**
   > y necesita que él actúe. Lo que te acaba de pedir en la conversación NO se avisa por
   > correo: se le cuenta ahí. Por eso `programar.py` lleva `--sin-aviso`.
   > **Excepción viva — Xavi Colomina (21/08/2026).** Gerard pidió autopublicar: sus posts se
   > crean EN FIRME y salen solos, sin revisión. Va por bandera `autopublicar` en
   > `config/metricool-marcas.json`, así que **no cambia nada para el resto del roster**.
   > Un error en un copy de Xavi se publica: revísalo antes, no después.
4. **Nunca toques los secretos**: `infra/.env`, `infra/.env.winston`.
5. Si cambias una **regla de negocio**, actualízala en *todos* los sitios donde vive (ver
   "Trampas" abajo).

## Los agentes

| Agente | Quién es | Ficha |
|---|---|---|
| **Winston / "Winy"** | Coordinador. Filtra todo antes de que llegue a Gerard, despacha trabajo y avisa. | `agentes/winston.md` |
| **Olivia / "Oli"** | Estratega. Decide QUÉ grabar: monta la tanda de apuestas del ciclo. **Corre sola** la noche martes→miércoles de la semana 📊 de cada cliente y deja las ideas en la Bandeja (`Autor = Oli`). A mano, si hace falta: `infra/olivia/olivia.sh <cliente>`. | `agentes/estratega.md` |
| **Coco** | Copywriter. Guioniza de madrugada y escribe los copies de RRSS. | `agentes/copywriter.md` |
| **Analista** | Análisis mensual de cierre → deck de Canva. Se arranca con `infra/analista/analista.sh`. | `agentes/analista.md` |
| **Editor** | Montaje de vídeo (skills `edicion-multicam`, `edicion-clips`). | `agentes/editor.md` |
| **QA / "Iris"** | Revisión antes de publicar. **Definido pero en stand-by**: no está enchufado a nada. | `agentes/qa.md` |
| **Nova** | Meta-agente: mantiene el propio sistema. **Propone y espera OK**, nunca aplica solo. | `agentes/nova.md` |

**Quién corre solo y quién no** (importante, se confunde): por cron van **Winy** (check-in),
**Coco** (guiones) y, desde el 22/09/2026, **Oli**: `com.rmagency.oli-noche` (miércoles 01:30)
corre `infra/olivia/oli_noche.py`, que monta la tanda de los clientes en su semana 📊 Analizar,
la sube a la Bandeja y avisa por WhatsApp **y** correo; `com.rmagency.oli-recordatorio`
(sábado 10:00) recuerda lo que siga sin revisar. **Freno (02/10/2026)**: si un cliente tiene
ideas de Oli en `Nueva`, no se genera tanda nueva para él (se avisa); las ideas no se acumulan.
Oli lee además el panel (`memoria/analisis/<cliente>.md` + `general.md`). **Analista, Editor y QA** siguen siendo
sesiones interactivas o fichas: nada los ejecuta de madrugada.

Clientes activos (21/09/2026): **jesus-mora, newmos, xavi-colomina** + **rm-agency** (cuenta propia,
fuera del reloj). **Ex-clientes**: golossa, midtown, msm, algoritmo — fuera de toda la config
(sus ids de Notion quedan en `exclientes` de `config/notion-bases.json`; fichas en `memoria/clientes/`
como historial y casos de venta). Respaldo de la limpieza: `memoria/_respaldo-limpieza-2026-09-21/`.
Plan vigente: `AUDITORIA-Y-PLAN-2026-09.md`.

## Dónde vive cada cosa

- `ciclos/YYYY-MM/<cliente>/manifest.json` — estado del ciclo por etapa (grabación → edición →
  distribución → cierre). Es el "bus" del sistema.
- `ciclos/YYYY-MM/<cliente>/hipotesis.json` — **el termómetro**: una hipótesis escrita por
  pieza y su resultado medido (explicado en `ciclos/HIPOTESIS.md`). Lo abre **Oli** al montar
  la tanda, y **Coco lo va rellenando solo** cada vez que guioniza.
- `agentes/guiones/ETIQUETAS.md` — **qué va en cada etiqueta** (Tipo de idea · Formato ·
  Plantilla · Palanca · Soporte): definiciones, listas CERRADAS y desempates. Fuente única desde
  el 02/10/2026 (antes se solapaban y lo medido no significaba nada). Se aplica en Notion con
  `infra/notion/etiquetas_sincronizar.py`.
- `agentes/guiones/` — cómo se escribe un guion. **Dos capas**: `_comun.md` + el Tipo
  (`viral.md`/`marca.md`, el objetivo) + la **Plantilla** (`plantillas/<nombre>.md`, la
  mecánica). La plantilla se guarda en Notion por pieza, y es lo que permite comparar
  formatos: `termometro.py --plantillas`. Catálogo y evidencia: `agentes/guiones/plantillas/README.md`.
- `memoria/clientes/<slug>/` — ficha, `marca.json`, brief de copy.
- `memoria/aprendizajes/registro.md` — aprendizajes, append-only.
- `memoria/clasificacion/<cliente>.md` — **con qué plantilla y metodología se hizo cada pieza
  publicada**. Es el puente Coco→Analista: el bruto de Metricool dice qué vídeo funcionó, esto
  dice qué tenía. Lo genera `infra/notion/clasificacion.py` cada noche.
- **Panel "Qué vídeos hacer"** (02/10/2026) — qué funciona en la agencia y por cliente, con botón
  para adaptar una idea ganadora a otro cliente (aceptar/rechazar con motivo → Bandeja).
  URL en `config/rutas.md`. Datos: `infra/analisis/panel_datos.py` → `memoria/analisis/`
  (`general.md` y `<cliente>.md` son lo legible; **el `panel.json` no se lee a mano**).
  Listas comunes: `agentes/guiones/ETIQUETAS.md` (ver arriba). `config/etiquetas.json` solo
  guarda lo propio de cada cliente ("Etiquetas del cliente"), lo que Gemini no usa (Oficio) y
  dónde se escribe cada etiqueta (siempre en la fila de rendimiento). Gemini ve los vídeos con
  `infra/analisis/ver_video.py`; `etiquetas_check.py` dice qué opción de Notion se sale.
  Marca RM del panel (fuente, logo, colores): `infra/analisis/marca/`.
  **Automático**: cada noche `noche.sh` mete los vídeos nuevos (rendimiento.py), Gemini los ve
  (ver_video.py, 10/cliente) y se recalcula el panel; cada mañana una tarea programada de la app
  de Claude republica la web (solo `datos.json`). Las propuestas (`memoria/analisis/propuestas.json`)
  se escriben a mano.
- `memoria/metricas/<cliente>.md` — resumen de métricas (**usa el .md, no el .json**).
  `memoria/metricas/_posts/<cliente>.json` es el índice de todas las publicaciones: dato de
  máquina para el termómetro, **no lo leas tú**.
- `config/` — `rutas.md` (repos externos), `metricool-marcas.json` y **dos fuentes únicas**:
  - `publicacion.json` — días de publicación + **pausas** + **excepciones** temporales por
    cliente (explicado en `calendario-publicacion.md`).
  - `ciclo-mensual.json` — **el reloj**: las 4 fases del mes y el desfase de cada cliente
    (explicado en `ciclo-mensual.md`).
  > Los `.md` de estos dos **solo explican, no repiten datos**. Para cambiar algo, toca el JSON.
- `INBOX-GERARD.md` — bandeja de avisos.
- `../notas/*.md` — notas sueltas de Gerard en Obsidian (fuera del hub, en el vault).

## Infra (automatismos, corren de madrugada)

- `infra/estado/estado.py` — **recolector de estado en Python puro (0 tokens)**. Reúne el
  reloj, ciclos, cobertura, notas y aprendizajes en `estado.txt`. Es lo que alimenta a Winy y
  al check-in: el modelo ya no explora, solo redacta. Si necesitas la foto del sistema, ejecútalo.
- `infra/estado/ciclo.py` — **el reloj**: qué fase toca a cada cliente esta semana
  (`--mes` para la rejilla entera). Sale solo dentro de `estado.py`.
- `infra/estado/termometro.py` — **el termómetro**: cruza las hipótesis de cada pieza con sus
  vistas reales contra la mediana del cliente. `--revisar` la enseña legible (**es la vista
  que se le pasa a Gerard**; el JSON no se lee a mano), `--cerrar` guarda resultados,
  `--etiquetas` agrega el histórico, `--plantillas` compara **mecánicas** e `--ideas` compara
  **Formato** del contenido (tips, top 10, comparación…), **Tipo de idea** y **Autor** (Gerard/Oli;
  sin cliente, cruzan todos). ⚠️ Desde el 22/09/2026 en Notion `Formato` = formato del contenido
  y `Soporte` = Reel/Carrusel/Story. Los
  agregados miden desde lo **publicado en Notion** (`memoria/clasificacion/_piezas/`), cruzado
  por fecha con Metricool — no desde las tandas, cuyos títulos no casan con Notion. Sus avisos salen dentro de `estado.py`. Ver `ciclos/HIPOTESIS.md`.
- `infra/olivia/olivia.sh <cliente> [YYYY-MM]` — arranca a **Oli** en sesión interactiva con su
  kickoff cargado, para montar la tanda del ciclo. No hay versión headless a propósito.
- `infra/estado/router.py` — carril 0: contesta consultas calculables sin llamar al modelo.
- `infra/responder/` — Winy conversacional por WhatsApp (`process.sh` = router de 3 carriles;
  `winy-system.md` = charla en Haiku; `winy-tareas.md` = tareas en Sonnet; `memoria.py` = 30 días).
- `infra/winston/winston-checkin.sh` — check-in diario 00:30 (Python recoge + Haiku redacta).
- `infra/metricool/` — `fetch_metricool.py` (métricas; **corre cada noche dentro de `notion/noche.sh`** desde el 22/09/2026 — antes no lo corría nadie y el termómetro no medía nada) y `chequeo_cobertura.py` (huecos sin programar).
- **"vamos a programar vídeos"** → sigue `infra/programacion/PROGRAMAR.md` (copy de Coco + vídeo de
  Drive → borrador en Metricool + email con el enlace). Redes, ajustes de YouTube y
  autopublicación salen POR CLIENTE de `config/metricool-marcas.json`: **Xavi va a
  IG+TikTok+YouTube Shorts y se publica solo**; el resto sigue en borrador.
- **Flujo de contenido en Notion** (idea → base cliente → guion → rodaje) → `infra/notion/CONTENIDO.md`.
  `com.rmagency.notion-noche` (00:45) corre `bandeja.py` + `distribuir.py` + `guionizar.py` (Coco
  guioniza según Tipo Viral/Marca, plantillas en `agentes/guiones/`). Mapa: `config/notion-bases.json`.
  ⚠️ **La fábrica solo arranca si alguien aprueba en la Bandeja** (Estado=Aprobada + Cliente).
  Si nadie lo hace, todo sale exit=0 diciendo "nada que distribuir" y el atasco es invisible:
  por eso `bandeja.py` cuenta lo parado y `estado.py` lo canta en el check-in.
- **Carruseles IA Golossa** (idea → prompt base → prompts por slide → Cloud Design por capas) →
  `infra/notion/CARRUSELES-IA-GOLOSSA.md`.
- `infra/olivia/referencias.py` — **creadores de referencia** (08/10/2026): de quién son los vídeos
  de referencia de la Bandeja/Contenido (TikTok solo; Instagram lo pone Gerard en «Creador ref» y el
  check-in se lo recuerda), sus mejores vídeos y por qué funcionan (Gemini). Base Notion
  «🎯 Creadores de referencia» (`creadores_db`); Oli lee `memoria/analisis/creadores/<cliente>.md`.
  Corre cada noche en `noche.sh`.
- `infra/web/blog.py` — **blog de rmagency.es** (WordPress en Hostinger): sube un artículo `.md` como
  **BORRADOR** (imagen destacada, categoría, extracto). `--publicar <id>` solo con «publica» de Gerard.
  Credenciales `WP_*` en `infra/.env`. Plan multicanal: `PLAN-MULTICANAL-RM-2026-10.md`.
- `infra/notifier/notify.sh` — cascada WhatsApp → email → INBOX.
- `infra/formato_wa.py` — pasa Markdown a formato WhatsApp (negrita con UN asterisco).

## Coste (importante)

Las llamadas automáticas van con `--tools ""`, `--system-prompt` propio y `--max-budget-usd`.
Sin eso, cada llamada arranca con ~24k tokens de system prompt y definiciones de herramientas.
**Si tocas un script de `infra/`, mantén esos flags.** Detalle en `infra/_jubilado/LEEME.md`.

En sesión interactiva: **Sonnet por defecto**, Opus a mano con `/model` solo para diseño de
verdad. No lances subagentes en cadena salvo necesidad: cada uno arranca con contexto frío.

## Trampas conocidas

- ~~El calendario de publicación vive en DOS sitios que deben coincidir~~ → **RESUELTO el
  11/08/2026.** Ahora hay **fuente única**: `config/publicacion.json` (días + pausas +
  excepciones temporales). Lo leen `chequeo_cobertura.py` y `programacion/calendario.py`.
  `config/calendario-publicacion.md` **solo explica, no repite datos**. Para cambiar un día,
  toca el JSON y nada más.
- El hub está en `~/rmagency/` (fuera de `~/Documents`) porque macOS no deja que los procesos
  de launchd lean `~/Documents`. Hay una copia muerta en `~/Documents/Claude/AGENTES RM`:
  **no es el sistema, ignórala**.
- ~~En este Mac, `python3` (3.12) no tiene certificados SSL~~ → **ARREGLADO el 11/08/2026.**
  Le faltaba el `cert.pem` que instala el `Install Certificates.command` de Python. Se creó
  el symlink a mano:
  `/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/cert.pem` → el `cacert.pem`
  de `certifi`. Ahora **los dos intérpretes hablan con Metricool**. Si algún día vuelve el
  error `CERTIFICATE_VERIFY_FAILED`, comprueba que ese symlink sigue vivo (una reinstalación
  de Python 3.12 se lo lleva por delante).
