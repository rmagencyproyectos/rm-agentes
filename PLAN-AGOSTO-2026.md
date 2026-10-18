# Plan de agosto 2026 — montar el motor

> **Ventana**: martes 11/08 → lunes 31/08 (20 días).
> **Decisión de Gerard**: *motor primero, clientes después.* El esfuerzo de agosto va a
> montar el sistema, no a producir contenido. En septiembre entran clientes nuevos y no
> puede volver a irse de las manos.
> **Origen**: `memoria/reuniones/2026-08-11-briefing-gerard.md`.

## El problema que estamos resolviendo

No es "falta contenido". Es esto, en palabras de Gerard:

1. **Se trabaja a picos.** Tres semanas de nada, y de golpe una avalancha de planificación
   y edición. Se va de culo para sacar los mismos números.
2. **No sabemos qué funciona.** Jesús Mora no ha funcionado nunca y no hay ni una hipótesis
   escrita de por qué. En Golossa vamos verdes en producto.
3. **Todo se hace a mano.** Ideas, guiones, decisiones: cada mes se reinventa desde cero.
4. **Vendemos visitas, no ventas.** El cliente paga bastante y no está claro que le salga.

El motor son **cuatro piezas** que atacan esos cuatro puntos, en ese orden.

---

## Pieza 0 — Arreglar el termómetro roto ✅ HECHO (11/08)

`estado.py --refrescar` no podía consultar Metricool: fallaba el certificado SSL en los
cinco clientes. A `python3` (3.12) le faltaba el `cert.pem` que instala el
`Install Certificates.command` de Python.

**Arreglado** con el symlink a `certifi`:
`/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/cert.pem`.
Ahora los dos intérpretes hablan con Metricool. Anotado en las trampas de `CLAUDE.md`.

De paso: `chequeo_cobertura.py` documentaba un `--dias N` que nunca leía (la ventana estaba
fija en 12 días). Arreglado también.

### Lo que destapó al arrancar

La cobertura llevaba tiempo devolviendo un **"todo cubierto ✅" que era mentira** (dato viejo
en caché). La foto real de los próximos 30 días:

| Cliente | Realidad |
|---|---|
| **Golossa** | El de mañana 12/08 está **en borrador** (no se publica solo). Después del 16/08, **nada**. |
| **Jesús Mora** | Tiene los **domingos** de agosto (16, 23, 30) pero **ningún miércoles**. Le falta la mitad del mes. |
| **MSM** | Después de mañana, **nada**. |
| **Midtown** | 2 jueves programados. En parón, pero el sistema le sigue exigiendo slots. |
| **Newmos** | 0. En parón, mismo problema. |
| **Xavi** | 0 — correcto, está ignorado hasta septiembre. |

### Estado "pausado" y excepciones ✅ HECHO (11/08)

Midtown y Newmos estaban en parón pero el sistema les seguía exigiendo slots: Winy habría
avisado de huecos falsos cada día hasta septiembre, que es justo como se aprende a ignorar
los avisos.

Ahora hay **fuente única**: `config/publicacion.json`, con tres conceptos —
**días**, **pausas** (no publica) y **excepciones** (publica otros días durante un rango).
Lo leen el chequeo de cobertura y el repartidor de slots. **Caducan solas**: el 1 de
septiembre todo vuelve a su ritmo sin tocar nada.

Cargado: Midtown en pausa todo agosto · Newmos en pausa sin fecha · Xavi en pausa hasta
septiembre · Jesús Mora solo domingos en agosto.

**Resultado**: de 5 avisos (3 falsos) a 2 avisos reales.

De paso se resuelve la trampa histórica de "el calendario vive en dos sitios que deben
coincidir": `config/calendario-publicacion.md` ya solo explica, no repite datos.

---

## Pieza A — El reloj 🕐 ✅ HECHO (11/08)

Cada cliente pasa por las mismas 4 fases cada mes (📊 analizar → ✍️ guiones → 🎬 grabar →
✂️ editar), pero **desfasados** entre sí. Con los tres clientes activos sale clavado:

|  | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **Xavi** | 📊 Analizar | ✍️ Guiones | 🎬 Grabar | ✂️ Editar |
| **Golossa** | ✍️ Guiones | 🎬 Grabar | ✂️ Editar | 📊 Analizar |
| **Jesús Mora** | 🎬 Grabar | ✂️ Editar | 📊 Analizar | ✍️ Guiones |

**Nunca coinciden dos grabaciones ni dos avalanchas de edición.** Cada semana hace siempre el
mismo tipo de trabajo; solo cambia el cliente. Ahí muere el pico.

Encaja con lo ya acordado: Jesús Mora graba en **S1 de septiembre** ("principios de
septiembre") sin haberlo forzado.

**Entregado**:
- `config/ciclo-mensual.json` — fuente única (fases + desfase por cliente).
- `config/ciclo-mensual.md` — la explicación.
- `infra/estado/ciclo.py` — `ciclo.py` (esta semana) y `ciclo.py --mes` (la rejilla).
- Enchufado a `infra/estado/estado.py`: **Winy lo cuenta en el check-in diario** sin que nadie
  pregunte.

**Fuera del reloj**: MSM (lo lleva Andrea), Midtown y Newmos (en pausa). Cuando Midtown
vuelva en septiembre, se le da **desfase 3** y encaja sin tocar a nadie.

> Nota: agosto es mes de transición y no cuadra del todo (Golossa graba el 17, que cae en S3
> y no en su S2). El reloj empieza a correr limpio en **septiembre**.

---

## Pieza B — El termómetro 🌡️ ✅ HECHO (11/08)

Cada pieza sale con una **hipótesis escrita** (`apuesta` + `porque`) y se compara con **lo
normal de ese cliente**: la mediana de sus vistas por red, excluyendo la propia tanda. La
persona escribe la apuesta; la máquina hace todo el trabajo con números.

Detalles que importan: **mediana y no media** (un reel viral se lleva el 90% del mes y deja
la media inservible); **se suman Instagram y TikTok** (el mismo vídeo puede salir x1.6 en una
y x0.2 en la otra el mismo día); y **no se juzga nada antes de 14 días**.

**Entregado**:
- `ciclos/YYYY-MM/<cliente>/hipotesis.json` — una hipótesis por pieza + su resultado.
- `ciclos/HIPOTESIS.md` — el bucle explicado.
- `infra/estado/termometro.py` — mide, `--cerrar` guarda, `--etiquetas` agrega el histórico.
- `fetch_metricool.py` ahora guarda **todas** las publicaciones en
  `memoria/metricas/_posts/<cliente>.json`. Antes solo el top-10, así que una pieza normal
  era invisible y no había nada que cruzar.
- Enchufado a `estado.py`: avisa **solo** cuando hay piezas con número.

### Lo que destapó al arrancar

Lo de **"a Jesús Mora no le funciona nada" es sobre todo una caída de TikTok**, no del
contenido. Mediana de vistas por mes:

| | junio | julio | agosto |
|---|---:|---:|---:|
| **TikTok** | 4.133 | 2.159 | 978 |
| **Instagram** | 1.186 | 1.260 | 1.527 |

Instagram está plano o subiendo. Lo que se ha hundido es TikTok. *(Agosto son solo 2 piezas:
la última bajada aún es débil.)* Anotado en `memoria/aprendizajes/registro.md`.

### Caso de prueba cargado

`ciclos/2026-09/jesus-mora/hipotesis.json` — **8 apuestas deliberadamente distintas**
(taller, POV, antes/después, precio, crítica, humor, a cámara, sin voz). Cada una tiene su
porqué y sus etiquetas. Es **una propuesta**: Gerard la revisa y decide.

La número 7 (Jesús a cámara) es el **control** del experimento: sabemos que "educar a cámara"
no funciona, pero *contar una historia* a cámara es otra cosa. Si falla, se cierra esa puerta
para siempre y se deja de discutir.

---

## Pieza C — La fábrica ⚙️ (que no se haga a mano)

**Qué es**: que las ideas y los guiones del mes salgan solos a partir del banco de ideas +
los aprendizajes + la ficha del cliente.

Buena noticia: **esto ya está medio montado y hay que auditarlo, no inventarlo**.
- `infra/notion/` — flujo idea → base de cliente → guion → rodaje. Corre cada noche a las
  00:45 (`distribuir.py` + `guionizar.py`, con Coco guionizando según Tipo Viral/Marca).
- `agentes/guiones/` — plantillas de guion.
- `Open-Generative-AI` + skill `/generate` — creatividades con IA al proveedor más barato.
- `infra/notion/CARRUSELES-IA-GOLOSSA.md` — carruseles por capas.

**Trabajo real**: ver qué de esto funciona hoy de verdad, arreglar lo que esté roto y
extenderlo a los cuatro clientes activos en vez de solo a Golossa.

### Auditoría (11/08) — la fábrica no está rota, está parada

Corre cada noche desde el 28/07. En 16 tandas ha producido **1 idea repartida y 0 guiones**.
Y no hay ni un error en el log: todo `exit=0`.

El motivo: **el único gate humano no se aprieta**. Había **14 ideas en la Bandeja en `Nueva`**,
todas de hace más de una semana, **5 con cliente ya puesto** — a un clic de salir guionizadas
esa misma noche. Sin ideas aprobadas, `distribuir.py` imprime "Nada que distribuir" y sale
con 0: todo verde, cinta vacía. **El mismo patrón que el SSL** — un fallo silencioso que se
lee como normalidad.

✅ **Arreglado**: `infra/notion/bandeja.py` cuenta lo atascado, corre el primero en `noche.sh`
y `estado.py` lo canta en el check-in. El gate deja de ser invisible.

⚠️ **Sin resolver — decisión de Gerard**: de esas 14, **11 son links de Instagram sin una
sola frase**. No son ideas, son marcadores. Triarlos obliga a abrir cada enlace y recordar por
qué se guardó, que es exactamente el trabajo que hace que no se trien nunca. Mientras eso no
se resuelva, la fábrica seguirá alimentándose sola de aire.

---

## Pieza D — El escaparate 📈 (solo diseño en agosto)

**Qué es**: decidir **qué número se le enseña al cliente** que no sea "visitas al perfil".

En agosto **solo se define**, no se implementa (decisión: primero ejecución). En septiembre
se monta. Xavi ya tiene la lente clara (leads al DM de Instagram); el resto no.

---

## Calendario de las 3 semanas

### Semana 1 · mar 11 → dom 17

- 🔴 **Jue 13, 15:00 — peaje: grabación del vídeo de presentación de Xavi.** Acotado: plan
  de grabación y guion a partir del borrador de Notion. Nada más.
- 🟠 **Lun 17 — peaje: grabación de Golossa en el obrador de Valls.** Acotado: lista de
  vídeos, sacada de lo que ya sabemos que funciona, adaptada al obrador.
- **Pieza 0**: arreglar el SSL de Metricool.
- **Pieza A**: diseñar el reloj y asignar el desfase por cliente.
- **Cuadrar el inventario real de Xavi** (¿21 piezas o ~40?). Bloquea su calendario.

### Semana 2 · lun 18 → dom 24

- **Pieza B**: el termómetro completo.
- **Pieza C**: auditoría y arreglo de la fábrica.

### Semana 3 · lun 25 → dom 31

- **Pieza D**: definir la métrica de cliente.
- 📅 **Jue 28 — reunión Midtown** (retoman en septiembre).
- **Cargar septiembre en el motor** — la prueba de fuego:
  - Calendario completo de Xavi (3-4 piezas/semana desde el 1 de septiembre).
  - Las 8 hipótesis de la tanda de Jesús Mora.
  - Ciclo de septiembre de Golossa.

Si el 31 de agosto septiembre está cargado en el sistema y no en la cabeza de Gerard, el
motor funciona.

---

## Deuda que arrastramos (a resolver por el camino)

- ⚠️ **Xavi publica 3-4/semana**, no mié+dom. Hay que cambiarlo en **los dos sitios**:
  `config/calendario-publicacion.md` y las `REGLAS` de `infra/metricool/chequeo_cobertura.py`.
- ⚠️ **Notas caducadas** en el sistema: "grabar con Jesús Mora antes del 12/08" (agosto ya
  está cubierto) y "grabar con Golossa" (ya hay fecha: 17/08).
- ⚠️ **Xavi sigue sin `copy-brief.md`** — es el único cliente activo sin él.
