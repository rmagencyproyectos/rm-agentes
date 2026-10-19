# Fábrica de carruseles — `carrusel.py`

De una **pieza JSON** a los PNG del carrusel (1080×1350) + **un PDF** con las mismas páginas
(para el documento de LinkedIn) + `_vista.png` (hoja de contacto para revisar de un vistazo).
Fase 1 de `PLAN-MULTICANAL-RM-2026-10.md`. Solo renderiza: **no sube nada** a Metricool, Notion
ni la web.

```bash
python3 infra/carruseles/carrusel.py --json pieza.json [--out DIR]
    --motor auto|playwright|chrome   # auto: Playwright si está instalado; si no, Chrome por CLI
    --navegador RUTA                 # o $CARRUSEL_CHROME: ruta del ejecutable de Chrome/Chromium
    --solo-validar                   # comprueba las reglas del brief y no renderiza
    --estricto                       # los avisos también paran (exit 1)
    --html                           # guarda el HTML de cada diapositiva (para depurar)
```

Salida (por defecto en `<carpeta del json>/<id>/`): `<prefijo>-01.png … -NN.png`, `<id>.pdf`, `_vista.png`.

## Instalación en el Mac de Gerard

Hace falta **un Chrome** (el de `/Applications/Google Chrome.app` vale, es el que ya usaba
`slides.js`) y **una** de estas dos:

1. **Recomendado:** `pip3 install playwright` — **no** hace falta `playwright install`: si
   Playwright no tiene navegador propio, el script tira del Google Chrome del Mac.
2. Sin Playwright: `pip3 install pillow` y `--motor chrome` (lanza Chrome headless por línea de
   comandos, una vez por diapositiva; ~3 s por diapositiva).

Pillow además genera `_vista.png` (si no está, se salta sin error).

⚠️ La corrida de noche (`infra/notion/noche.sh` → `guionizar.py`) usa **`/usr/bin/python3`** (el del
sistema, 3.9). Es a ese al que hay que instalarle el paquete:
`/usr/bin/python3 -m pip install --user playwright` (o `pillow` para el motor chrome). El código es
compatible con 3.9 (comprobado). Si falta todo, la fábrica guarda los textos igual, lo avisa en
`INBOX-GERARD.md` y deja en la ficha de Notion el comando para renderizar a mano.

Dónde busca el navegador, por orden: `--navegador` → `$CARRUSEL_CHROME` → (motor playwright) su
Chromium → Google Chrome / Chromium en `/Applications` → `google-chrome`/`chromium` en el PATH →
`$PLAYWRIGHT_BROWSERS_PATH` (o `~/Library/Caches/ms-playwright`).
En la nube de Claude: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` (ya preinstalado).

Fuentes: Glacial sale de `infra/analisis/marca/` (marca RM); Instrument Serif (estilo personal,
licencia OFL) está en `plantilla/fuentes/`. Se incrustan en el HTML: no dependen del sistema.

## Archivos

| Archivo | Qué es |
|---|---|
| `carrusel.py` | CLI, validación (`validar()`, la usa también Coco multicanal), HTML y render |
| `dibujos.py` | los tipos de dibujo (maquetas) del estilo RM, como funciones de datos → HTML |
| `plantilla/rm.css` | el CSS de la plantilla a mano (`memoria/clientes/rm-agency/carruseles/_fuente/carruseles.html`), extraído tal cual |
| `plantilla/personal.css` | estilo de la cuenta personal de Gerard |
| `ejemplos/` | piezas de prueba: `04-dar-valor.json`, `06-ayudar.json` (los carruseles hechos a mano, pasados a datos; salen igual que los PNG originales) y `personal-capitol-1.json` (con fotos de mentira en `ejemplos/fotos/`) |

---

## Esquema — estilo `rm` (cuenta de RM Agency)

Reglas del `memoria/clientes/rm-agency/copy-brief.md`: máx. **10 diapositivas**, sin logo ni
contador, fondo gris siempre, la última al revés (#ff2041), hilo de preguntas, portada que habla
del que lee, venta solo al final con «Comenta ESTRATEGIA». La plantilla ya hace todo lo visual:
el JSON solo lleva textos y dibujos.

```jsonc
{
  "id": "04-dar-valor",            // obligatorio: nombre de la pieza (carpeta y PDF)
  "prefijo": "c4",                 // opcional: nombre de los PNG (por defecto, el id)
  "estilo": "rm",
  "cifras_verificadas": ["20.000", "443.000"],  // opcional: si está, avisa de cada cifra que no esté aquí
  "portada": {
    "rotulo": "Negocios de Lleida",              // rótulo pequeño arriba
    "cifra": "20.000",                           // opcional: número gigante en rojo
    "titular": "…taller de muebles *de Lleida.*",// *…* = palabra marcada
    "apoyo": "Si un taller puede, tu negocio también.",  // opcional
    "pregunta": "¿A quién le interesan los muebles?",    // opcional: botón de abajo (hilo)
    "regalo": false                              // opcional: «🎁 Al final, algo gratis…»
  },
  "diapositivas": [                // entre 1 y 8
    {
      "rotulo": "…",               // solo se ve si la anterior NO dejó pregunta
      "titular": "A todo el mundo. Todos tenemos *el mueble de la abuela.*",
      "apoyo": "…",                // opcional, línea de apoyo
      "pregunta": "¿Y qué hicimos con eso?",  // opcional: abajo; la siguiente la repite arriba
      "solo_pregunta": false,      // opcional: la diapositiva es solo la pregunta anterior en grande
      "dibujo": { "tipo": "ilustracion", "nombre": "comoda", "preguntas": ["¿Cuánto vale?"] }
    }
  ],
  "cierre": {                      // la última, fondo rojo
    "titular": "Si quieres saber qué podrías enseñar tú, *te lo decimos.*",
    "apoyo": "Gratis.",
    "etiqueta": "Comenta",         // opcional (por defecto «Comenta»)
    "palabra": "ESTRATEGIA",       // opcional (por defecto «ESTRATEGIA»)
    "despues": "Gratis.",          // opcional, debajo de la palabra
    "pie": "te escribimos por mensaje"  // opcional (por defecto este)
  }
}
```

**Marcado**: `*texto*` = la palabra clave. En la paleta v2 (14/10) el titular sale en rojo y lo
marcado en oscuro; en la portada igual. `\n` = salto de línea. Todo lo demás se escapa (no se
puede meter HTML en los textos).

**Hilo de preguntas**: la `pregunta` de cada diapositiva sale abajo como botón; la siguiente la
repite arriba como rótulo. Sin pregunta, abajo sale «desliza →» y arriba el `rotulo`.

### Tipos de dibujo

| tipo | campos | ejemplo de uso |
|---|---|---|
| `barras` | `barras: [{cifra, etiqueta, color?, alto?}]`, `ancho?` | comparar cifras (8.400 vs 89.679). `color`: gris·medio·oscuro·rojo (por defecto la mayor en rojo); `alto` en %, si no, proporcional |
| `pantallas` | `pantallas: [{red, cifra, icono?: play\|ojo, destacada?}]` | un vídeo y sus visualizaciones (móvil en rojo si `destacada`) |
| `lista` | `items: [texto]` | checklist con ticks rojos |
| `ranking` | `items: [{texto, cifra}]`, `pie?` | top 3 de vídeos |
| `cadena` | `pasos: [texto]`, `destacado?` (índice, por defecto el último), `compacta?` | Valor → Autoridad → **Marca** |
| `notas` | `titulo`, `barra?`, `lineas?: [texto \| {texto, tachado?, negrita?}]`, `cursor?`, `vacias?`, `reloj?` | bloc de notas («Lo que sé y mis clientes no») |
| `buscador` | `consulta?` (o `barra?`), `nombre`, `detalle`, `sello?` | búsqueda + resultado con sello «Referente» |
| `aviso` | `titulo`, `texto`, `lineas_borrosas?` | alerta roja «Cuidado con esto» |
| `tachados` | `botones: [texto]` | botones de venta tachados («Compra ya») |
| `compartir` | `titulo?`, `contactos: [nombre \| {nombre, inicial}]`, `enviado?` | menú «Enviar a…» |
| `chat` | `mensajes: [{quien, texto, inicial?, lado?: izq\|der, color?}]` | lo que dicen los negocios |
| `whatsapp` | `contacto`, `estado?`, `mensajes: [{texto, hora}]` | chat de WhatsApp |
| `movil` | `hora`, `fecha?`, `notificaciones: [{app, texto, gris?}]` | pantalla de bloqueo |
| `comentarios` | `comentarios: [{quien?, texto, respuesta?}]` | comentarios de un post |
| `bandeja` | `mensajes: [texto]`, `barra?`, `contador?` | bandeja de mensajes con globo «750» |
| `etiquetas` | `items: [texto]`, `destacada?` (índice) | nube de ideas |
| `pasos` | `pasos: [{etiqueta, texto, estado?: on\|apagado}]` | línea de tiempo / episodios |
| `episodios` | `items: [texto \| {texto, on}]` («···» = puntos) | rejilla de episodios |
| `programacion` | `barra?`, `filas: [{hora, texto, on?, nuevo?}]` | parrilla de la tele |
| `ruta` | `desde`, `hasta`, `distancia?` | Lleida ··· Tarragona |
| `ab` | `desde`, `hasta` | del punto A al B |
| `youtube` | `titulo?`, `estado?`, `requisitos: [{texto, valor, pct?}]` | monetización |
| `llamada` | `nombre?`, `estado?` | llamada entrante |
| `reels` | `reels: [cifra \| {cifra, destacado}]` | rejilla de reels con uno destacado |
| `ilustracion` | `nombre: comoda\|casa`, `preguntas?: [texto]` | dibujo fijo con preguntas flotando |
| `html` | `html` | **escape a mano**: HTML tal cual. Coco no lo usa (la validación avisa) |

Cualquier dibujo admite además `reacciones: [texto]` (globos encima, hasta 4) y `nota` (texto
rojo a mano, inclinado).

Para un dibujo nuevo: función en `dibujos.py` + entrada en `TIPOS` + fila en esta tabla (y en
`agentes/guiones/multicanal.md`, que es la lista que ve Coco).

### Validación (`validar()`)

- **Error** (no renderiza): más de 10 diapositivas · falta titular en portada/diapositiva/cierre ·
  tipo de dibujo que no existe · cualquier precio (`€`).
- **Aviso** (renderiza; con `--estricto`, para): portada con «nosotros/nuestro/RM Agency» · CTA
  antes del cierre · palabra distinta de ESTRATEGIA · dibujo `html` · pregunta de más de 42
  caracteres (sale en dos líneas) · cifra que no está en `cifras_verificadas` (si la pieza trae
  esa lista; en la fábrica multicanal esto es **error**).

**Encaje automático**: si un dibujo no cabe en su hueco (titular de tres líneas…), la plantilla lo
encoge lo justo para no pisar el pie. Con los carruseles hechos a mano no salta.

## Coco multicanal (Fase 2)

`multicanal.py` es la parte sin Notion de la fábrica: prompt (`agentes/guiones/multicanal.md` +
brief de RM), parseo y validación de la respuesta de Coco, y la carpeta
`memoria/clientes/rm-agency/carruseles/<NN>-<id>/` (pieza.json, copy.md, linkedin.md, blog.md con
el frontmatter de `infra/web/blog.py`, PNG, PDF). Lo llama `infra/notion/guionizar.py` cuando la
idea de RM trae `Soporte = Multicanal`. Para probar a mano sin Notion ni modelo:

```bash
python3 infra/carruseles/multicanal.py --prompt --idea "…" --notas "…"        # ver el prompt
python3 infra/carruseles/multicanal.py --respuesta crudo.json --idea "…" --notas "…" --out /tmp/x
```

---

## Esquema — estilo `personal` (cuenta personal de Gerard, fotos, en catalán)

Limpio y distinto del de RM: papel cálido, serif, la foto manda. Estructura fija:
**portada** (foto a sangre + gancho encima) → por cada foto, **texto que la presenta** + **la foto**
→ **cierre** oscuro con la pregunta a los fotógrafos y «Capítol N, aviat».

```jsonc
{
  "id": "personal-capitol-1",
  "estilo": "personal",
  "serie": "Fotos que no vaig publicar",   // opcional: rótulo pequeño arriba
  "capitulo": 1,                           // opcional: «… · Capítol 1»
  "portada": {
    "foto": "fotos/portada.jpg",           // ruta relativa al JSON (o absoluta)
    "gancho": "Aquesta foto gairebé *no existeix.*",   // *…* = cursiva
    "apoyo": "Tres fotos i el que hi ha darrere."      // opcional
  },
  "fotos": [                               // cada una = 2 diapositivas (texto + foto)
    {"texto": "Primer, la que vaig estar a punt d'esborrar.", "foto": "fotos/01.jpg",
     "pie": "Lleida, gener",               // opcional, peu de foto
     "encaje": "completa"}                 // completa (sin recortar, con marco; por defecto) | llena (a sangre)
  ],
  "cierre": {
    "pregunta": "Fotògrafs: quina foto vau estar a punt *d'esborrar*?",
    "apoyo": "Explica-m'ho als comentaris.",  // opcional
    "capitulo": 2,                            // opcional: por defecto capitulo + 1
    "aviat": "Capítol 2, aviat"               // opcional: sustituye el texto entero
  }
}
```

Validación: gancho, texto de cada foto y pregunta del cierre obligatorios; las fotos tienen que
existir; Instagram admite 20 diapositivas (avisa si pasa de 10).

### Estructura de los carruseles de fotografía (Gerard, 19/10/2026)

Se hacen **a partir de la transcripción del reel gemelo + las fotos que elige Gerard**:

1. **Portada** (`portada.gancho`): el gancho del reel, sacado de la transcripción.
2. **Contexto** (`intro.texto` + `intro.avis`): el contexto del día y el aviso «veureu X fotos de…».
3. **Por cada foto** (`fotos[]`): una diapo que explica la foto según lo que dice en el reel
   (`texto`) y la foto **a pantalla completa** (en las variantes netes, `encaje` = `llena` por defecto).
4. **Final** (`cierre.pregunta` + `cierre.preguntes`): el CTA — quina us agrada més i per què,
   què he fet malament, què he fet bé, on m'equivoco.

Variante `cartel` (la elegida y **la de por defecto**; principio de Gerard: súper minimalista, solo textos imprescindibles y stickers): **nada por los bordes** (ni serie, ni día, ni firma, ni números,
ni flechas). Como mucho un `sticker` por diapo: texto corto o un icono `:camera:`, `:pluja:`,
`:flash:`, `:sol:`, `:cotxe:`, `:estrella:`, `:cor:`. Ejemplo: `ejemplos/personal-cap2-cartel.json`.
Fuentes de Gerard (Architype R., Lazydog, Rocket Brush) en `plantilla/fuentes/propias/`, fuera de git.
