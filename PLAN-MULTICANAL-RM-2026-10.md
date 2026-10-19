# Plan — Fábrica multicanal de RM (una idea → todos los canales)

> Pedido por Gerard el 14/10/2026. Objetivo: que **una idea** de RM salga sola convertida en
> carrusel de Instagram/TikTok/Facebook, post de LinkedIn y artículo del blog, con **un único
> OK de Gerard** antes de programar. Lo máximo automático posible, sin inventar datos.

## 1. Punto de partida (lo que ya existe y se reutiliza)

| Pieza | Estado hoy | Se reutiliza para |
|---|---|---|
| **Bandeja de Ideas RM** (Notion) → `Contenido RM` → Coco guioniza de madrugada | Funciona para vídeo | Entrada única de ideas también para la fábrica multicanal |
| **Plantilla de carruseles** (`memoria/clientes/rm-agency/carruseles/_fuente/`) | Funciona a mano: los datos están metidos en el código | Render automático de los PNG a partir de un JSON |
| **Reglas de RM** (`copy-brief.md`): que no huela a venta, portada que hable del que lee, hilo de preguntas, máx. 10 diapositivas, paleta | Escritas | Prompt de Coco y validación |
| **Metricool, marca RM** (5747122) | Conectadas: **Instagram, TikTok, Facebook y página de empresa de LinkedIn** | Programar todo desde un solo sitio, en borrador |
| **Datos reales de clientes** (Metricool por marca, también ex-clientes) | Se pueden consultar | Cifras verificadas para los casos (nunca inventadas) |
| **Gate de Gerard** ("programa" = en firme) | Regla vigente | El único paso humano |

Lo que falta: (a) que el carrusel se genere desde datos, no a mano; (b) que Coco escriba
LinkedIn y blog además del copy; (c) que `programar.py` sepa subir **imágenes** y mandar a
**varias redes**; (d) un destino para el blog (ver preguntas abiertas).

## 2. El modelo: una pieza madre, cinco salidas

```
IDEA (Bandeja, Cliente = RM)
   │  + datos verificados (Metricool / lo que diga Gerard)
   ▼
PIEZA MADRE  ── la historia en hilo de preguntas: portada (habla del que lee) → 6-9 pasos → moraleja → CTA
   ├─► Carrusel IG  (PNG 1080×1350, plantilla RM)        ─┐
   ├─► Carrusel TikTok (mismas imágenes, modo foto)       ├─ Metricool, un post multi-red, BORRADOR
   ├─► Facebook (mismas imágenes + copy)                 ─┘
   ├─► LinkedIn (texto largo en primera persona + el carrusel como PDF)  → Metricool, BORRADOR
   └─► Blog (artículo 800-1.200 palabras, SEO local Lleida)              → web, BORRADOR
```

La pieza madre es lo que hoy hacemos a mano en cada carrusel. Todo lo demás **se deriva** de
ella; no se reescribe la idea cinco veces.

### Cómo se adapta a cada canal

| Canal | Formato | Tono y reglas | Frecuencia propuesta |
|---|---|---|---|
| **Instagram** | Carrusel ≤10 + copy corto + 4-5 hashtags | Portada que identifique; venta solo al final («comenta ESTRATEGIA») | Mié + Dom 15:00 (lo actual) |
| **TikTok** | Mismo carrusel en modo foto + música | Igual que IG; primera línea del copy = portada | Igual que IG |
| **Facebook** | Mismas imágenes + copy de IG | Público local algo mayor; sin hashtags de más | Igual que IG |
| **LinkedIn** | Texto 1.200-1.800 caracteres + carrusel en PDF (documento) | Primera persona de Gerard, empresario a empresario. Gancho en la 1.ª línea, párrafos de 1-2 frases, la lección explícita, CTA suave («si te ha pasado, escríbeme»). Sin enlaces en el cuerpo | Mar + Jue 9:00 |
| **Blog/web** | Artículo con H1, intro, datos, proceso, lección, FAQ, CTA | SEO local: «redes sociales para empresas en Lleida», «marketing de contenidos Lleida»… Caso real sin nombre del cliente | 1 por semana (el viernes) |

## 3. El flujo automático, paso a paso

1. **Idea** → Gerard la suelta en la Bandeja (WhatsApp a Winy o Notion) con `Cliente = RM` y
   `Soporte = Multicanal`. Si es un caso real, una línea con los datos que conoce.
2. **Aprobar** (el gate que ya existe) → `Estado = Aprobada`.
3. **De madrugada** (`noche.sh`):
   1. `datos_caso.py` — si la idea cita un cliente, saca de Metricool las cifras (vídeo más
      visto, media, seguidores) y las deja como **datos verificados**. Coco solo puede usar
      esas cifras o las que haya escrito Gerard.
   2. **Coco multicanal** (una sola llamada, Sonnet, con `--tools ""` y tope de gasto) devuelve
      un JSON con: la pieza madre (diapositivas), los copies de IG/TikTok/FB, el post de
      LinkedIn y el artículo del blog. Se valida contra las reglas del brief (≤10 diapositivas,
      portada sin «nosotros», sin precios, cada cifra en la lista de verificadas).
   3. `carrusel.py` renderiza los PNG desde ese JSON (la plantilla actual, sin datos en el código)
      y un PDF con las mismas páginas para LinkedIn.
   4. Todo se cuelga en la ficha de Notion: imágenes, copies, LinkedIn y blog, y la ficha pasa a
      **📦 Listo para revisar**.
4. **Gerard revisa una sola ficha** por la mañana y la marca `Aprobado` (o la corrige ahí mismo).
5. **Programación**: `programar.py` crea en Metricool los borradores en las fechas libres de
   cada canal (según `config/publicacion.json`) y el blog en borrador en la web. Si Gerard dice
   «programa» en la conversación, se firma todo de una vez (regla del 09/10).
6. **Medición**: el termómetro ya mide IG/TikTok; se le añade LinkedIn y las visitas del blog.
   Las piezas que funcionen en redes se reciclan (ver punto 5).

**Resultado:** de idea aprobada a borradores en los cinco canales en una noche, con un solo
clic de Gerard por pieza.

## 4. Qué hay que construir (por fases)

### Fase 0 — Probarlo a mano (esta semana, sin código)
- Con los **7 carruseles ya hechos** (Desliza si, cliente perdido, dar valor, series, ayudar,
  inmobiliaria, y el reel de Lleida) escribir a mano su **post de LinkedIn** y su **artículo de
  blog**. Sirve para fijar el tono de LinkedIn y del blog **antes** de automatizar: lo que
  Gerard corrija aquí se convierte en las reglas del prompt.
- Decidir las preguntas abiertas (sección 7).

### Fase 1 — Carruseles desde datos + Metricool multi-red (≈1 sesión)
- ✅ **19/10/2026: `infra/carruseles/carrusel.py` hecho** (PNG + PDF desde JSON, estilos `rm` y
  `personal`; 04-dar-valor y 06-ayudar pasados a datos y comprobados contra los PNG originales).
  Falta lo de `programar.py` (imágenes + varias redes).
- `infra/carruseles/carrusel.py --json <pieza>.json` → PNG + PDF. Sale de la plantilla actual;
  las diapositivas pasan a ser datos (tipos de dibujo: barras, chat, móvil, lista, cadena…).
- `programar.py`: soportar **imágenes** (la subida ya está probada hoy con los carruseles) y
  **varias redes en un post** (IG + TikTok + FB; LinkedIn aparte por su texto propio).
  ⚠️ Probar primero el carrusel de fotos en TikTok vía API: no está verificado.

### Fase 2 — Coco multicanal (≈1 sesión)
- ✅ **19/10/2026: prompt + gancho hechos** — `agentes/guiones/multicanal.md`,
  `infra/carruseles/multicanal.py` y `guionizar.py` (`Soporte = Multicanal`, solo `rm-agency`).
  Probado con una llamada real (Sonnet, ~105 s + una corrección de 41 s). Pendiente: lo de Notion
  (abajo, lo hace Gerard), `datos_caso.py` y subir los PNG a la ficha (hoy quedan en disco).
- `agentes/guiones/multicanal.md`: el prompt con las reglas de RM (sale del `copy-brief.md`).
- `guionizar.py`: si `Soporte = Multicanal`, pide el JSON completo en vez del guion de vídeo.
- Notion, base `Contenido RM`: propiedades nuevas `Canales` (multi-select), `LinkedIn` (texto),
  `Blog` (página hija) y la vista **📦 Listo para revisar**.
- `datos_caso.py`: cifras verificadas desde Metricool por marca.

### Fase 3 — Blog y calendario por canal (≈1 sesión)
- ✅ **14/10/2026: conector del blog hecho y probado** — `infra/web/blog.py`, contraseña de
  aplicación activa (usuario agency.wizzads@gmail.com). Primer borrador: post 795 (caso pastelería).
- **La web es rmagency.es: WordPress en Hostinger** (comprobado el 14/10/2026: la API REST
  responde y el blog está **vacío**, empieza de cero). Conector `infra/web/blog.py` que crea el
  artículo **en borrador** vía `wp/v2/posts`, con imagen destacada (la portada del carrusel).
- Para poder escribir hace falta una de dos (lo hace Gerard, nunca un agente):
  (a) **contraseña de aplicación** en WP (Usuarios → Perfil → Contraseñas de aplicación) guardada
  en `infra/.env` — hoy la web no la anuncia, puede que un plugin de seguridad o Hostinger la
  tenga desactivada; o (b) **conectar Jetpack** (ya instalado) a la cuenta
  rmagency.proyectos@gmail.com de WordPress.com, y entonces se escribe con el conector de WordPress.
- `config/publicacion.json`: entrada `rm-agency` con días por canal (hoy RM usa el `_default`).
- `chequeo_cobertura.py`: avisar si un canal se queda sin piezas programadas.

### Fase 4 — Reciclaje (continuo)
- Cada semana, el termómetro elige la pieza de IG/TikTok que mejor ha funcionado y, si no tiene
  versión de LinkedIn o blog, la manda a la fábrica. Esto cubre lo que pediste: que LinkedIn y
  el blog salgan **de lo que ya ha funcionado en redes**, no solo de ideas nuevas.

## 5. Contenido: los pilares y el banco de ideas

Sale de lo que ya tenemos hecho y medido.

| Pilar | Qué cuenta | Ya tenemos | Ideas siguientes |
|---|---|---|---|
| **Casos reales** (sin nombre) | Un cliente, un problema, cifras reales | Pastelería (2.000→11.000, 2,4 M), taller de muebles (20.000 en 6 meses, YouTube monetizado), costura (+4 M en 50 episodios), maquinaria (aviso de estafa, ×10), inmobiliaria (750 comentarios) | Cada uno da también un artículo de blog «caso de éxito» y un post de LinkedIn «lo que aprendí» |
| **Método** | Cómo pensamos el contenido | Dar valor, series, ayudar sin pedir nada | Ganchos, la portada que identifica, por qué no grabar «lo que me gusta a mí», el termómetro (medir con hipótesis) |
| **Identificación** | El empresario se reconoce | «Desliza si…» | «Desliza si eres hostelero…», «…si tienes una clínica…» (uno por sector) |
| **Lleida** | Somos de aquí | Reel «Lleida, hemos llegado» | Negocios de Lleida que lo hacen bien (con permiso), errores típicos del comercio local |
| **Detrás de RM** | Cómo trabajamos | — | Un día de rodaje, cómo montamos un mes de contenido, el reel «Me cuelo en empresas» |

**Un ejemplo completo** — idea: *«El taller de muebles: dar valor»*
- IG/TikTok/FB: el carrusel que ya está hecho (10 diapositivas) + copy.
- LinkedIn: «Un taller de muebles llegó a 20.000 seguidores en seis meses. No vendiendo:
  enseñando.» → qué vídeos funcionaron y por qué → la lección (enseñar da autoridad) → «¿Qué sabe
  tu empresa que tus clientes no saben?».
- Blog: «Cómo un taller de restauración llegó a 20.000 seguidores enseñando lo que sabe» — con
  los tres vídeos más vistos, el proceso, y una FAQ («¿qué publico si mi sector es aburrido?»).

## 6. Reglas que no cambian (y que el sistema valida solo)

- **Nada se envía ni se publica solo.** La fábrica deja borradores; en firme solo con «programa».
- **Datos**: solo cifras verificadas (Metricool o dichas por Gerard). Nada de nombres de
  clientes ni títulos reales de sus vídeos.
- **Venta solo al final**, en una línea. CTA común: «comenta ESTRATEGIA» (redes) /
  «escríbeme» (LinkedIn) / formulario (blog). Se cumple por privado: Gerard pide empresa e
  Instagram y responde con una lluvia de ideas en un audio.
- **Coste**: las llamadas automáticas con `--tools ""`, `--system-prompt` propio y
  `--max-budget-usd`. Una llamada por idea para los cinco canales.

## 7. Decisiones de Gerard (14/10/2026)

1. **Web**: rmagency.es (WordPress en Hostinger), enlazada en Metricool como web + feed RSS
   (`rmagency.es/feed`). Metricool **lee** el blog (analítica y autopublicación del RSS en redes)
   pero **no crea artículos**. Flujo: el artículo se deja escrito y listo para pegar → Gerard lo
   publica en WP → Metricool lo comparte por RSS en LinkedIn/Facebook. Para que lo suba un agente
   haría falta una contraseña de aplicación de WP (opcional, más adelante).
2. **LinkedIn**: desde la **página de empresa** (la conectada en Metricool).
3. **Voz** en LinkedIn y blog: **«nosotros»** (la agencia).
4. **Facebook**: **activo**. Los carruseles salen en IG + FB (+ TikTok cuando se verifique el modo foto).
5. **Ritmo**: OK — 2 carruseles/semana en redes + 2 posts de LinkedIn + 1 artículo de blog.
6. **«Gerard RM»** (TikTok @algorritmo_rm): **va aparte, no se toca**. La fábrica es solo de RM Agency (5747122).
