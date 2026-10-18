# Prompts jubilados (2026-07-26)

Los reemplazó el rediseño de coste (router de 3 carriles):

- `responder-prompt.md` → ahora `infra/responder/winy-system.md` (carril 1, charla) y
  `infra/responder/winy-tareas.md` (carril 2, tareas).
- `winston-prompt.md` → ahora `infra/winston/winston-voz.md`.

Los viejos invitaban al modelo a explorar el hub con Glob/Read, y cada invitación era un
turno más de bucle agéntico. Los nuevos reciben el estado ya recogido por
`infra/estado/estado.py` y solo redactan.

Se guardan por si hay que consultar el texto original. No los usa nadie.
