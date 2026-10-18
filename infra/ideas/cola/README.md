# Bandeja de salida de ideas (cola)

Winy (en modo tarea) **no ejecuta** `idea_add.py` — en modo headless no tiene permiso para
correr comandos. En su lugar **escribe aquí** un `.json` por cada idea que hay que guardar en
Notion. Después, `process.sh` (bash normal, sin gate de permisos) recoge estos `.json`, los sube
a la Bandeja de Ideas RM con `idea_add.py --from-json`, y borra el que sube bien.

Formato de cada archivo (`idea-<lo-que-sea>.json`):

```json
{
  "idea": "Reel enseñando el cheesecake de pistacho paso a paso",
  "cliente": "golossa",
  "soporte": "Reel",
  "formato": "Tips",
  "tipo_idea": "Educativa",
  "autor": "Gerard",
  "origen": "link IG/TikTok",
  "referencia": "https://www.instagram.com/p/....",
  "objetivo": "",
  "gancho": "",
  "guion": ""
}
```

Solo `idea` es obligatorio. `cliente` y `formato` deben ser valores válidos (si no, se ignoran).
`soporte` (Reel/Carrusel/Story/TikTok/Otro) **no tiene valor por defecto**: cuando la idea viene
de un link, lo deduce `infra/ideas/video_link.py` de la URL (`/reel/` → Reel, `/p/` → Carrusel);
si no se sabe, el campo se omite y se rellena en Notion. `formato` es el formato **del
contenido** (Tips, Top 10, Comparación…) desde el 22/09/2026; un JSON viejo con
`"formato": "Reel"` se sigue entendiendo como soporte. `autor` por defecto es `Gerard`.
Esta carpeta debería estar casi siempre vacía: es solo un buzón de paso.
