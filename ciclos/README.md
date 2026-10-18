# ciclos/ — el "bus" de coordinación

Un directorio por **ciclo mensual** (`YYYY-MM/`) y dentro uno por **cliente**. Cada
cliente tiene un `manifest.json` (estado por etapa, lo lee y despacha Winston) y una
subcarpeta por etapa donde cada agente deja su output:

```
YYYY-MM/<cliente>/
  manifest.json     # estado por etapa + campo "despacho" (qué agente actúa ahora)
  estrategia/       # shotlist.md (Estratega)
  edicion/          # punteros + metadatos de las piezas (Editor) — NO los vídeos
  copies/           # copy por pieza (Copywriter)
  qa/               # veredictos/incidencias (QA)
```

## Cómo se pasan el output
Nadie llama a nadie: cada agente **lee** el manifest, hace su parte, **escribe** su
subcarpeta y **actualiza su casilla** + el campo `despacho`. Winston, en su check-in,
inspecciona los manifests y despacha lo `pendiente` (poll = sustituto de los "eventos").

## Estados por etapa
- `estrategia`: `pendiente | listo | aprobado_por_gerard`
- `grabacion`: `pendiente | hecha`
- `edicion`: `pendiente | en_curso | listo`
- `copies`: `pendiente | listo`
- `qa`: `pendiente | ok | bloqueado`
- `distribucion`: `pendiente | aprobado_gerard | programado`  ← Gates 2 y 3 = Gerard
- `cierre`: `pendiente | hecho`

> El campo `aprobado_gerard` en `estrategia` y `distribucion` es la marca de que se cruzó
> una puerta 🚪. Ningún agente lo pone a `true` por su cuenta.
