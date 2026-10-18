# Ficha de cliente — Xavi Colomina

> Fusión de `FABRICA/clientes/xavi-colomina/perfil.md` (rico) + memoria. Es el **cliente
> piloto** (único con pipeline de vídeo de punta a punta). Brief de copy: `copy-brief.md`
> (derivado de esta ficha el 19/08/2026, pendiente de validar con Gerard/Xavi).

## Identidad
- **Slug**: xavi-colomina
- **Sector**: pádel (entrenador / coach de alto nivel)
- **Protagonista**: Xavi Colomina
- **Idioma**: español (algún tramo en catalán en las fuentes)
- **Temática**: culturizar al jugador — técnica, táctica y **mentalidad**. Tono
  didáctico-retador.

## Negocio
- **Diferencial**: técnica + mentalidad/psicología (filosofía de vida). Esa es la pata a
  sobre-explotar. Regla editorial: en cada pieza de técnica, añadir **qué mentalidad tener**
  y cómo afecta en pista.
- **Segundo ángulo**: desmontar mitos / "lo que nunca te enseñan".
- **Servicios**: (1) formación de técnicos, (2) diagnóstico por vídeo (jugador manda vídeo
  al DM de IG → Xavi corrige), (3) clubs (clínicos, asesoría de escuelas, formación de
  plantilla).
- **Lente de métrica**: alcance y retención (fase de autoridad). Los leads al DM dejan de
  ser objetivo de contenido el 07/09/2026; los servicios siguen existiendo, pero el copy
  no los nombra.

## Contenido
- **Líneas**: master class por movimiento (rulo a la reja, bandeja, smash, bolea, defensa);
  mitos/"lo que no se enseña"; podcast (pesa la mentalidad, va a YouTube, intercalado).
- **Formatos validados**: multicam en pista ✅; análisis de vídeo (Xavi marca el error en
  primer plano) ✅ preferido. Talking-head ⚠️ sin soporte visual; pizarra/animación ⚠️ baja
  prioridad.
- **Banco de ideas aprobadas**: posición en ataque (mito del primer palo), revés a dos
  manos, empuñadura no continental, bascular en el fondo, sentido común en el pádel.
- **Registro de performance**: Notion "Registro de contenido — qué funciona" (dentro de la
  página Xavi Colomina). Métricas duras en Metricool.

## Material — cómo trabajarlo
- **Fuentes**: `/Volumes/DD 2 TB WORK/Xavi Colomina/Videos/` (`Podcast/`, `Entreno Pablo:Phineas/`).
- **Setup cámaras**: Podcast = 2 cám 16:9 (`IMG_2561` general + `IMG_9457` cerrada, offset
  audio **+4.131 s**). Entreno multicam = `POV/` (sigue a Xavi) + `IMG_249X.MOV` (fija del
  jugador, audio de solapa) → skill `edicion-multicam`.
- **Transcripción**: `scripts/edit/transcribe.mjs` → AssemblyAI por defecto (acierta
  "pádel"), Whisper de fallback. Quirks solo con Whisper: `padre→pádel`,
  `Cineas/Fíneas→Phineas`, bucles de repetición y ruido inicial.
- **Criterio de momento clave**: lección clara y aplicable; frases quotables de mentalidad.

## Marca visual (valores duros en `marca.json`)
- Título **VarsityTeam-Bold** (mayúsculas) + subtítulos **Montserrat-Black**.
- Amarillo `#F2C94C` + blanco; sin caja negra (drop-shadow). 1080×1920 @ 60fps.
- Título-gancho de 3 partes (amarillo / 1 palabra blanca / remate amarillo). **Sin kicker.**
- Fuente de verdad del estilo: `REMOTION/src/CaptionedVideo/` + `edicion-clips/references/estilo.md`.

## Tono, CTA y hashtags
- **Voz**: didáctico-retador; nada de clickbait vacío.
- **Ganchos aprobados**: "EL PÁDEL / NO / SE PIENSA", "TU CUERPO / TE / DELATA",
  "EL TALENTO / NO / TE SALVA", "MEDIO GAS / SE / MEMORIZA".
- **CTA**: **ninguno** (Gerard, 07/09/2026). Los copys no llevan cierre de venta ni nada que
  pueda parecerlo — sin DM, sin diagnóstico, sin firma. Cierran en la última línea de
  contenido. Fase de autoridad, no de captación. Regla en `copy-brief.md` § 3.

## Entrega y distribución
- **Entrega**: `…/Video Editado IA/` (entreno) o `…/Edición Video Automatica/` (podcast histórico).
- **Naming**: `Xavi Colomina - {Gancho}.mp4`.
- **Canales**: Instagram (principal), TikTok, YouTube Shorts; podcast en YouTube largo.
- **Cadencia**: 3/semana desde el **01/09/2026** — martes, jueves y domingo a las 15:00.
- **Estrategia desde el 04/10/2026** (Gerard, tras el panel "Qué vídeos hacer"):
  - **Martes y jueves → tips o consejos técnicos/tácticos.** Es lo que mejor le funciona:
    Explicación ×2,5, palanca Problema ×2,6, gancho de error/mito ×2,5.
  - **Domingo → resumen del vídeo largo de YouTube** que se sube ese mismo domingo.
  - **El reto de la mano izquierda baja**: era 2/3 de lo publicado y rendía ×0,9. Deja de ser
    una pieza diaria; si sale, va dentro del resumen del domingo.

## Qué funciona — ángulos a explotar (de los datos de Golossa, 30/09/2026)

> Cuatro mecánicas medidas sobre 253 piezas. Detalle y evidencia en
> `agentes/guiones/plantillas/README.md` ("Los dos ejes"). Traducción para este cliente:

- **Secreto del oficio** (interacción, `secreto-del-oficio`): lo que mira un entrenador en los
  tres primeros golpes · su rutina exacta antes de competir · el detalle técnico que no se
  enseña en las clases de grupo.
- **Opinión marcada** (comentarios, `opinion-marcada`): "la mayoría entrena lo que ya le sale
  bien" · "el material no te va a arreglar el revés". Sin CTA, según su brief.
- **Día de trabajo** (alcance, `pov-trabajador`): una sesión real en pista, entrenando.
- **Caso real + ubicación** (alcance, `caso-real`): un alumno concreto y su club o ciudad.

**Y en todas:** grabar en el sitio de trabajo real trabajando, y **decir la ubicación en voz
alta** cuando la pieza tenga sitio (la gente de esa ciudad se queda). Ver `agentes/guiones/_comun.md`.

## Estado / aprobados
- **Memoria**: [[pipeline-edicion-skills]], [[edicion-multicam-skill]].
- **Estado**: Entreno Pablo/Phineas C1-C5 entregados, **C6-C12 pendientes**. Podcast: C4
  entregado, C2/C3/C5/C6/C10 pendientes.
- **Pendiente**: validar `copy-brief.md` con Gerard/Xavi;
  comparativa AssemblyAI vs Whisper.
