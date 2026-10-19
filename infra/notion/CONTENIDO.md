# Flujo de contenido en Notion — de la idea al rodaje

Montado el 28/07/2026. Sustituye al caos de 7 bases con esquemas distintos: ahora hay UNA
bandeja de entrada y UNA base por cliente, todas con el mismo esquema limpio.

```
Bandeja de Ideas RM  →  Contenido <Cliente>  →  ⚡ botón  →  Coco guioniza (00:45)  →  🎬 A grabar  →  Metricool
   (todo cae aquí)        (apruebas + tipas)                                        (agrupado por sitio)
```

## Las piezas

- **Bandeja de Ideas RM** (`Agencia Marketing`) — entrada única. Todo idea/link entra aquí con
  Estado `Nueva`. Winy la llena desde WhatsApp (`idea_add.py`). Vistas: 📥 Sin triar · ✅ A repartir · 📚 Histórico.
- **Etiquetas de la idea** (22/09/2026) — `Tipo de idea` (Educativa, Humor, Tendencia…),
  **`Formato`** del contenido (Tips, Top 10, Ranking, Comparación…) y **`Autor`** (Gerard, Oli,
  Andrea, Cliente), en la Bandeja **y** en cada base de cliente. ⚠️ Reel/Carrusel/Story ya no es
  "Formato": es **`Soporte`**. Las pone Winy si se ven claras, si no las pones tú al aprobar, y si siguen vacías
  **Coco las rellena al guionizar** (nunca pisa lo que haya puesto una persona). Son abiertas:
  añade opciones nuevas en Notion y ya valen; si Coco crea una, te avisa para que la fusiones
  si sobra. Es lo que mide `termometro.py <cliente> --ideas`. Fuente: `etiquetas_idea.py`.
- **Contenido \<Cliente\>** (una por cliente, dentro de su página) — el destino. 12 props:
  Idea · **Tipo** (Viral/Marca) · Resolución · Guion · Producción · Gancho (0-3s) · Palanca · CTA ·
  Copy RRSS · Soporte (Reel/Carrusel) · Formato (tips, top…) · Tipo de idea · Autor · Ubicación · Publicación · Notas. Vistas: 📥 Nuevas · ✍️ Guion · 🎬 A grabar (Prod=Pendiente
  de grabar) · ✂️ A editar (Prod=Grabado, para el editor) · 📦 Listo para programar (Prod=Editado) ·
  🗓 Calendario.
- **Paneles internos globales** (en `Agencia Marketing`): 🎬 A grabar, ✂️ Edición y
  **🖊️ Falta desglose** — juntan a todos los clientes con vistas enlazadas, para trabajar
  (grabar / editar / desglosar) de un vistazo.
- Mapa de ids: `config/notion-bases.json`.

**Privacidad**: cada cliente vive SOLO en su propia base `Contenido <Cliente>`; sus vistas solo
muestran lo suyo. Los paneles globales (🎬 A grabar, ✂️ Edición) son **de uso interno del equipo**
y NUNCA se comparten con un cliente (mezclan a todos). Al cliente, si acaso, se le comparte su base.

## El día a día

1. **Idea nueva** → cae en la Bandeja (Estado `Nueva`). La revisas en 📥 Sin triar.
2. **Aprobar** → le pones Cliente + `Tipo` (Viral/Marca) y Estado `Aprobada`. **Este es el único
   gate humano** (colapso de 1 noche, 28/07): ya no hay una segunda revisión en la base del cliente.
3. Esa **misma madrugada**, `noche.sh` hace TODO seguido: `distribuir.py` la baja a
   `Contenido <Cliente>` ya como `Resolución = Aprobada` + `Guion = Coco a guionizar` (y marca
   la Bandeja `Distribuida` + `Ficha`, idempotente); y `guionizar.py`, justo después, la guioniza.
4. A la mañana la idea está en **🎬 A grabar** con el guion escrito (gancho + beats + CTA según el
   `Tipo`) **y el copy de redes ya puesto en `Copy RRSS`**. La `Ubicación` la pones tú al revisar la tarjeta ya guionizada (agrupa el tablero).
5. **Grabas** con la vista 🎬 (agrupada por Ubicación). Marcas `Producción = Grabado` → desaparece.
6. Editas → `Editado` (aparece en 📦 Listo para programar) → al programar en Metricool pasa a
   `Programado` con su fecha en `Publicación` (vista 🗓 Calendario).

**Urgente (sin esperar a la noche):** WhatsApp a Winy **"guioniza ya la de Golossa"** (o
`infra/notion/guioniza-ya.sh golossa`) → reparte + guioniza al momento. Lo detecta el **carril 0.5**
de `process.sh` (`parse_guioniza.py`), corre en bash puro, 0 tokens. El botón **⚡ Guionizar** de
Notion queda como opcional (re-guionizar o ideas creadas directas en el cliente).

## ⚠️ El gate humano es el cuello de botella real

Comprobado el **11/08/2026**: la fábrica llevaba desde el 28/07 corriendo cada noche sin
producir **nada**. No estaba rota — estaba parada en el paso 2. Había **14 ideas en la
Bandeja en estado `Nueva`**, cinco de ellas con cliente ya puesto, esperando un clic que
nadie sabía que había que dar.

El fallo de diseño no era el código, era que **nadie lo decía**: sin ideas aprobadas,
`distribuir.py` imprime "Nada que distribuir" y sale con 0. Todo verde, cinta vacía. Mismo
patrón que el SSL de Metricool: un fallo silencioso que se lee como normalidad.

Arreglado con `bandeja.py`, que cuenta lo atascado y lo deja en `_bandeja.txt`; `estado.py`
lo lee y Winy lo canta en el check-in diario.

**Segundo problema — el link pelado.** De esas 14 ideas, **11 eran links de Instagram sin una
sola frase** ("Referencia de Reel guardada sin descripción"). No son ideas, son marcadores.

Coco **no puede abrir un enlace** (comprobado el 14/08/2026: los metadatos de Instagram vienen
vacíos sin login). Si la idea es solo el link, se niega — y hace bien: inventarse el vídeo es
peor que no hacerlo.

**Resuelto a medias el 26/08/2026.** Antes esa negativa llegaba como `no encontré JSON en la
respuesta`, que parece una avería, y la ficha volvía a la cola para fallar otra vez la noche
siguiente. Ahora:

1. `guionizar.py` reconoce la negativa (`parece_falta_desglose`) y aparca la ficha en
   `Guion = "Falta desglose"` — **fuera de la cola**, no se reintenta ni se gasta otra llamada.
2. Todas salen juntas en el panel **🖊️ Falta desglose — Global**, un bloque por cliente.
3. Gerard escribe 2-3 líneas en `Notas` (qué pasa · dónde está el giro · por qué funciona) y
   **no toca nada más**: `recuperadas()` las devuelve solas a la cola en la corrida siguiente.

Lo que sigue sin resolver es lo de fondo: **nadie va a desglosar 11 marcadores viejos**. El
panel al menos los pone en un sitio y en bloque, en vez de gotear un aviso por noche.

## Automatización

`com.rmagency.notion-noche` (LaunchAgent, **00:45**, detrás del check-in de 00:30) corre
`noche.sh` → `bandeja.py` + `distribuir.py` + `guionizar.py` + `autoprogramar.py`. Todo de
madrugada, como el resto.

⚠️ Lo lanza launchd (bash normal). NUNCA el responder headless: `claude -p --permission-mode
acceptEdits` no puede ejecutar Bash. Mismo patrón que `process.sh`.

## Cómo guioniza Coco

Instrucciones en markdown EDITABLE (se afinan con el uso): `agentes/guiones/_comun.md` (espina:
gancho 0-3s → retención por bucles abiertos → CTA) + `viral.md` (humor/impacto, CTA suave) o
`marca.md` (informa/resuelve, CTA directo) según `Tipo`. Coco se apoya en el `copy-brief.md` y las
métricas del cliente. Devuelve JSON (gancho, palanca[], beats[], cta, copy_rrss, notas_rodaje).

**El copy de redes viene con el guion** (26/08/2026). Antes lo escribía `autoprogramar.py` semanas
después, con el título como única fuente; ahora sale en la misma pasada y se guarda en `Copy RRSS`.
Al programar se **reutiliza** ese: solo se genera uno nuevo si el campo está vacío.
⚠️ Regla: el copy se escribe desde la **IDEA y las NOTAS de Gerard**, no desde los beats del guion.
El guion es un borrador que él va a retocar antes de grabar; la idea ya está dada por buena, así que
es lo único estable a lo que anclar el copy.

## Calendario ↔ Metricool

- **No solapar**: `calendario.py` pregunta a Metricool qué días ya tienen contenido y los salta.
- **Stock**: `chequeo_cobertura.py` añade a cada cliente 📦 editadas sin programar · 🎬 a grabar ·
  ✍️ sin guion. Eso es "hasta cuándo tenemos material".
- **Reflejar en Notion**: `programar.py --notion` marca `Programado` la fila que case por título
  (solo si hay coincidencia única; opt-in porque el vídeo de Drive y la idea de Notion no comparten id).

## Pasos manuales que solo hace Gerard (una vez)

1. **Compartir las bases nuevas con la integración interna "Winy RM"** (la del token de
   `infra/.env`). Lo más rápido: en Notion, página `Agencia Marketing` → ··· → Connections → añadir
   "Winy RM"; las bases hijas heredan. **Sin esto, `distribuir.py`/`guionizar.py` dan 404.**
2. **Instalar el LaunchAgent**:
   `cp infra/launchd/com.rmagency.notion-noche.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.rmagency.notion-noche.plist`
3. **Botón ⚡ Guionizar** en cada base (la API no crea botones): `+` → Button → *Edit property* →
   `Guion` = `Coco a guionizar`. Opcional: sin él, se pone el desplegable a mano.

## Bases viejas

Se dejaron intactas (Ideas GOLOSSA, WorkFlow Newmos, TABLA DE IDEAS de Jesús Mora, Idees Contingut
de Midtown…). No migramos nada: quedan de consulta y se pueden archivar cuando Gerard quiera.

## Multicanal (RM, 19/10/2026)

Si una idea de **Contenido RM** trae `Soporte = Multicanal`, `guionizar.py` no escribe guion de
vídeo: Coco devuelve en una llamada el **carrusel** (como datos), el **copy** IG/TikTok/FB, el
**post de LinkedIn** y el **artículo del blog** (`agentes/guiones/multicanal.md`). Se valida contra
el brief de RM (máx. 10 diapositivas, sin precios, portada sin «nosotros», solo cifras que estén
en la Idea/Notas — si falla, una corrección en la misma corrida y, si no, vuelve a la cola), se
renderiza con `infra/carruseles/carrusel.py` en `memoria/clientes/rm-agency/carruseles/<NN>-<id>/`
(PNG + PDF + copy.md/linkedin.md/blog.md) y se cuelga en la ficha: `Copy RRSS`, `LinkedIn` (si la
propiedad existe), el cuerpo con diapositivas/LinkedIn/blog y `Guion = Listo`. Nada se publica ni
se programa. **Las cifras verificadas son las que Gerard escribe en Idea/Notas**: si no las pone,
Coco no puede usar ninguna.

