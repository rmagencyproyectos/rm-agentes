# El termómetro — hipótesis, números y aprendizaje

> Cómo se sabe qué funciona. Los datos viven en `ciclos/YYYY-MM/<cliente>/hipotesis.json`;
> este fichero explica el bucle. La herramienta es `infra/estado/termometro.py`.

## El problema que resuelve

Se publicaba, se miraban las vistas y se opinaba. "Jesús Mora no funciona" es una frase que
llevaba meses circulando **sin una sola hipótesis escrita detrás**: nadie había apuntado
nunca por qué creía que un vídeo iba a funcionar, así que cuando funcionaba (o no) no se
aprendía nada. El mes siguiente se volvía a empezar de cero.

## El bucle

```
   escribir la hipótesis  →  publicar  →  medir  →  aprender  →  ideas del mes siguiente
        (persona)                        (máquina)   (persona)          ↑
                                                                        └── y vuelta a empezar
```

**La persona escribe solo lo que una máquina no puede**: la apuesta y el porqué.
**La máquina hace todo el trabajo con números.** Si se le pidiera a Gerard que estimara
vistas a mano, dejaría de hacerlo en dos semanas.

## Qué se escribe por pieza

| Campo | Qué es |
|---|---|
| `titulo` | Cómo se llama la pieza, para reconocerla |
| `plantilla` | **La mecánica** con la que se contó (`agentes/guiones/plantillas/`). Es lo que permite comparar formatos entre sí y entre clientes |
| `apuesta` | **La variable que se está probando.** Qué tiene esta pieza que las demás no |
| `porque` | Por qué creemos que va a funcionar. Aquí es donde se aprende |
| `etiquetas` | Palabras reutilizables (`humor`, `pov`, `precio`…). Es lo que acumula memoria |
| `publicado` | La fecha, cuando se publica. **Es la llave del cruce con las métricas** |
| `resultado` | Lo rellena el termómetro. No se toca a mano |

> **Quién escribe qué** (13/08/2026): **Oli** abre la tanda al montar el ciclo (objetivo,
> restricciones, riesgos, descartadas). **Coco** rellena `plantilla`/`apuesta`/`porque`/
> `etiquetas` de cada pieza en el momento de guionizar, así que ninguna pieza puede producirse
> sin hipótesis aunque a alguien se le olvide. Una pieza **ya medida no se reescribe**:
> cambiarle la apuesta a posteriori invalida justo lo que se estaba midiendo.

Una buena `apuesta` es **falsable**: "humor de situación actuado" se puede confirmar o
tumbar. "Contenido de más calidad" no.

## Cómo se mide

La pieza se compara con **lo normal de ese cliente en esa red**, no con un número inventado.

- El listón es la **mediana** de sus publicaciones (180 días), por red y formato.
  Mediana y no media porque un solo reel viral se lleva el 90% del mes y deja la media
  inservible como referencia.
- La tanda que se está midiendo **se excluye de su propio listón**. Si no, se estaría
  comparando consigo misma.
- Si el mismo vídeo salió en Reels **y** en TikTok, se **suman las dos**: vistas y listones.
  Una red puede tocarle la lotería y la otra no; sumando se cancela.
- Una pieza no se juzga hasta **14 días** después de publicarse (TikTok sigue repartiendo
  durante semanas).

| Ratio | Veredicto |
|---|---|
| ≥ 2.0 | 🟢🟢 pegó |
| ≥ 1.2 | 🟢 por encima |
| 0.8 – 1.2 | ⚪ en su media |
| < 0.8 | 🔴 por debajo |

## Cómo se usa

```bash
python3 "infra/estado/termometro.py"                                  # qué toca cerrar
python3 "infra/estado/termometro.py" jesus-mora --revisar              # leer la tanda entera
python3 "infra/estado/termometro.py" jesus-mora                       # la tanda en curso
python3 "infra/estado/termometro.py" jesus-mora --cerrar               # guarda resultados
python3 "infra/estado/termometro.py" jesus-mora --etiquetas            # qué funciona, histórico
python3 "infra/estado/termometro.py" jesus-mora --plantillas          # qué MECÁNICA le funciona
python3 "infra/estado/termometro.py" --plantillas                     # ídem, cruzando clientes
python3 "infra/estado/termometro.py" golossa --nueva --ciclo 2026-10   # tanda nueva
```

Necesita las métricas descargadas: `infra/metricool/fetch_metricool.py` escribe
`memoria/metricas/_posts/<cliente>.json` (**todas** las publicaciones, no solo el top).

El estado diario avisa solo cuando hay piezas con número, así que nadie tiene que acordarse.

## Dónde encaja en el reloj

En la fase **📊 analizar** (ver `config/ciclo-mensual.md`): se cierra la tanda del mes
anterior, se escribe el aprendizaje en `memoria/aprendizajes/registro.md`, y **de ahí salen
las ideas del mes siguiente**. Ese es el enganche: sin él el termómetro es un informe bonito
que nadie usa.

## Lo que el termómetro NO hace

- **No decide.** Dice qué pasó; qué se hace con eso lo decide una persona.
- **No mide ventas.** Mide alcance contra el propio historial del cliente. La métrica de
  negocio es otra pieza (`PLAN-AGOSTO-2026.md`, pieza D).
- **No concluye con una pieza.** Una etiqueta con una sola medición se marca como tal.
  Hacen falta varios meses; por eso las etiquetas se reutilizan entre tandas.
