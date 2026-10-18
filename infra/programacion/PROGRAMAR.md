# Runbook — "vamos a programar vídeos"

Cuando Gerard dice **"vamos a programar vídeos"** (de un cliente), el objetivo es dejar en
Metricool un **borrador por vídeo** con **el copy de Coco** como texto y **el vídeo de Drive
adjunto** (REEL). Nada se publica: se crean BORRADORES y Gerard los revisa en el planner.

## Pasos

1. **Listar los vídeos del cliente** (Drive):
   ```bash
   /usr/bin/python3 infra/programacion/listar_videos.py --cliente <cli> > ciclos/<ciclo>/<cli>/programacion/videos.json
   ```
   Gerard elige/ordena cuáles se programan (recorta el `videos.json` a esos).

2. **El copy**: desde el 26/08/2026 Coco ya lo escribe al guionizar y vive en `Copy RRSS` de
   la ficha de Notion. **Cópialo de ahí**; solo escríbelo de cero (desde
   `memoria/clientes/<cli>/copy-brief.md`) si esa pieza no lo trae
   (el brief manda sobre todo). Por cada vídeo:
   - Añade el copy al campo **`copy`** de su entrada en `videos.json` (ese es el texto del post).
   - Deja el registro en `ciclos/<ciclo>/<cli>/copies/NN_slug.md` con frontmatter **`fecha:`** =
     la fecha de publicación asignada en el paso 3 (así la retención lo borra tras esa fecha).
   - Actualiza la etapa `copies` del `manifest.json`.

3. **Asignar fechas + construir el payload**:
   ```bash
   /usr/bin/python3 infra/programacion/calendario.py --cliente <cli> \
     --videos-json ciclos/<ciclo>/<cli>/programacion/videos.json \
     --out ciclos/<ciclo>/<cli>/programacion
   ```
   Escribe `metricool.json` con `texto` (copy) + `drive_id` por post. La lista concisa de stdout
   (para el cliente) sigue usando el título corto, no el copy.

3b. **Portada de cada vídeo** (regla de Gerard, 09/10/2026): la miniatura tiene que ser el
   momento en que **se lee el texto principal** del vídeo (el título grande del gancho), completo
   y ya quieto, no a media animación. Se mira el vídeo y se elige el milisegundo:
   ```bash
   /usr/bin/python3 infra/programacion/portada.py --drive-id <id>              # hojas, 1 fotograma/s
   /usr/bin/python3 infra/programacion/portada.py --drive-id <id> --fino 2.4   # afinar cada 0,2 s
   /usr/bin/python3 infra/programacion/portada.py --drive-id <id> --frame 3.6  # confirmar en grande
   ```
   Abre las imágenes (Read), elige y escribe `"portada_ms": 3600` en el post de `metricool.json`.
   `programar.py` lo manda como `videoCoverMilliseconds`; el preview lo marca `🖼️` y avisa de los
   vídeos sin portada. `firmar.py` la conserva al pasar a firme. Para cambiar la de un post ya
   creado: PUT con los campos editables + `videoCoverMilliseconds` (como hace `firmar.py`).
   ⚠️ Cada PUT a Metricool **cambia el id del post**: actualiza `Metricool ID` en Notion.

4. **Preview** (no toca Metricool) y, con el OK, **crear los borradores**:
   ```bash
   /usr/bin/python3 infra/metricool/programar.py --in ciclos/<ciclo>/<cli>/programacion            # preview
   /usr/bin/python3 infra/metricool/programar.py --in ciclos/<ciclo>/<cli>/programacion --confirmar # crea BORRADORES
   ```
   El preview marca `🎬` (vídeo) y `✍️` (copy) y avisa de lo que falte. **Nunca `--publicar`**
   sin OK explícito de Gerard.

   ⚠️ **`--sin-aviso` si esto lo está pidiendo Gerard en la conversación** (regla suya,
   22/09/2026): el email solo tiene sentido para lo que pasa **solo, de madrugada**, y que él
   no puede saber que ha pasado. Si te lo acaba de pedir, ya lo sabe: se lo cuentas ahí y punto.

5b. **Pasarlo a firme**: el borrador ya creado no hace falta borrarlo y rehacerlo —eso volvería
   a subir el vídeo—, se firma en su sitio:
   ```bash
   /usr/bin/python3 infra/metricool/firmar.py --cliente <cli> --id <id_metricool> [--dry-run]
   ```
   A partir de ahí Metricool lo publica solo a su hora.
   **Regla de Gerard (09/10/2026): cuando él dice "programa" en la conversación, es programar
   DEL TODO** → borrador + `firmar.py` en el mismo paso, para que salga solo. No hace falta
   preguntarle "¿lo firmo?". Esto vale solo para lo que pide él en conversación: los
   automatismos (cron) siguen dejando borradores y **nada se firma por iniciativa propia**.

5. **Gerard revisa/edita** los borradores en el planner de Metricool.

## Gates (no se cruzan solos)
- El copy lo escribe Coco desde el brief; **Gerard lo revisa en el borrador** de Metricool.
- Los automatismos solo crean **BORRADORES**. En firme solo si Gerard lo pide: "programa" en
  la conversación ya cuenta como ese OK (ver 5b).
- Todo lo automático (retención de copies) corre **de madrugada**, nunca de día.

## Retención de copies
El registro `copies/NN_slug.md` se guarda solo **hasta su `fecha`**. Cada madrugada,
`infra/mantenimiento/limpiar_copies.py` (launchd `com.rmagency.limpiar-copies`, 03:30) borra los
vencidos para no acumular. Prueba a mano: `limpiar_copies.py --dry-run`.

## Notas
- Interpretador: **`/usr/bin/python3`** (el único con SSL en este Mac; python3.12 falla contra
  Metricool y Drive).
- Requisitos ya configurados: `GOOGLE_SA_JSON`, `METRICOOL_*`, y para el email `SMTP_USER`/
  `SMTP_PASS`/`EMAIL_DESTINO` en `infra/.env`.
- Clientes sin carpeta en Drive (MSM, Xavi): añadir su id a `config/drive-carpetas.json` primero.
