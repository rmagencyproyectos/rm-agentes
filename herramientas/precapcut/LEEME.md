# precapcut: vídeos medio editados en CapCut, por fases

Deja el proyecto de CapCut medio hecho para que Gerard (o Andrea o Jaume) le dé el toque final.
Se revisa **después de cada fase**: los subtítulos y los sonidos se montan sobre cortes ya aprobados,
así no se descuadran.

| Fase | Qué hace | Estado |
|---|---|---|
| 1 · Cortes | Transcribe en local con tiempos por palabra, quita tomas falladas, arranques en falso, muletillas y silencios, y lo monta en CapCut | **hecha** |
| 2 · Subtítulos | 1-2 palabras por bloque desde la misma transcripción, palabras clave resaltadas, estilos por marca | pendiente |
| 2b · Recursos | Iconos o emojis según lo que se dice («carpeta» → carpeta estilo iOS con el nombre) y fotos obligatorias donde se mencionan | pendiente |
| 3 · Sonido | Librería RM de efectos (Mixkit/Pixabay) colocados según el contenido | pendiente |
| 4 · Humano | Lo creativo, en CapCut | — |

## Cómo se pide

«Pre-edita los vídeos C0038 a C0041 de `<carpeta>` en el proyecto de CapCut «X»». Claude sigue esto:

1. `python3 precapcut.py fase1 <pieza> <vídeos en orden de grabación> [--idioma es|ca]`
   - `<pieza>` = nombre corto sin espacios (p. ej. `jesus-2026-10-26`). Todo queda en
     `~/rmagency/work/precapcut/<pieza>/`.
2. **Leer solo `fase1.md`** (tabla de frases ✓/✗). Nunca abrir el vídeo ni `transcripciones.json`.
   Revisar con criterio lo que el script no ve:
   - Si dos frases dicen lo mismo con otras palabras, quedarse con la mejor (normalmente la última).
   - Frases sueltas fuera del guion («¿grabas?», «vale, otra vez», «corta») → fuera.
   - Para cambiar algo, editar `decisiones.json` (`queda`: true/false) con un script corto.
3. `python3 precapcut.py montar <pieza> --en "<proyecto CapCut vacío>"` (o `--nuevo "<nombre>"`).
   **CapCut tiene que estar cerrado.** Hace copia del proyecto en `<pieza>/backups/` antes de escribir.
   Deja también `preview.mp4` (baja resolución) y `edl.csv`.
4. `python3 precapcut.py qa <pieza>` → re-transcribe el preview y lista palabras comidas o sobrantes
   (`qa-fase1.md`). Revisar las que caen en un borde de corte. Regla de Gerard: **no se presenta
   nada sin QA propio** (silencios, frases a medias, cortes a mitad de palabra).
5. Avisar a Gerard: duración bruto → montado, cuántas tomas fuera, frases dudosas, y que abra el
   proyecto en CapCut. **Esperar su OK antes de la fase 2.**

## Reglas

- Coste: el modelo solo lee `fase1.md` / `qa-fase1.md`. Transcripción, cortes y render son locales.
- No se sube audio a ningún servicio (nada de `capcut caption --cloud`).
- CapCut congelado en la **9.5**: la 10 rechaza los proyectos escritos por capcut-cli.
- Si una palabra sale mal siempre (nombres, marcas), añadirla a `vocabulario.txt`.

## Instalar en otro ordenador

- Mac: `bash instalar-mac.sh` · Windows: `instalar-windows.ps1`. Instala capcut-cli, faster-whisper
  y el modelo `medium` (~1,5 GB la primera vez).
- La carpeta de proyectos de CapCut se detecta sola (Mac: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`,
  Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`).

## Ajustes (arriba de `precapcut.py`)

`PAD_ANTES` 0,08 s y `PAD_DESPUES` 0,15 s de margen alrededor de cada palabra; `PAUSA_MAX` 0,35 s de
pausa permitida dentro de una frase; `SIM_TOMA` 0,6 de parecido para dar una frase por repetida.
