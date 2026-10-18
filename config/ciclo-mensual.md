# El reloj — el ciclo mensual de RM Agency

> Por qué existe y cómo se lee. **Los datos viven en `config/ciclo-mensual.json`**
> (fuente única). Este fichero explica, no repite.

## El problema que resuelve

Se trabajaba **por eventos**: "toca grabar" → avalancha de planificación, luego avalancha de
edición, luego tres semanas muertas hasta el siguiente pico. Todos los clientes a la vez.
Resultado: se iba de culo para sacar los mismos números.

## La idea

Cada cliente pasa por **las mismas 4 fases** cada mes:

| | Fase | Qué se hace |
|---|---|---|
| 📊 | **Analizar** | Leer las métricas del mes, escribir qué se ha aprendido y sacar las ideas del siguiente |
| ✍️ | **Guiones** | Guionizar las ideas aprobadas y cerrar la lista de tomas y la logística |
| 🎬 | **Grabar** | Grabar |
| ✂️ | **Editar** | Montar, copys, QA y dejarlo programado en Metricool |

Pero **desfasados** entre sí. Cuando Xavi graba, Newmos edita y Jesús Mora analiza. Así
**cada semana hace siempre el mismo tipo de trabajo**, solo cambia el cliente.

Nunca coinciden dos grabaciones. Nunca coinciden dos avalanchas de edición. El pico
desaparece porque la carga es la misma todas las semanas.

## Cómo se reparten las semanas

`S1` = días 1-7 · `S2` = 8-14 · `S3` = 15-21 · `S4` = 22 a fin de mes.

Los meses de 30-31 días alargan la S4. Es a propósito: mejor una semana larga que una quinta
semana suelta que descuadre el desfase de todos.

## Cómo se consulta

```bash
python3 "infra/estado/ciclo.py"          # qué toca esta semana
python3 "infra/estado/ciclo.py" --mes    # la rejilla del mes entero
```

Además sale **solo** en el estado diario (`infra/estado/estado.py`), así que Winy lo cuenta
en el check-in sin que nadie pregunte.

## Quién está en el reloj

Solo los clientes con **desfase** en el JSON. Ahora mismo: **Xavi, Newmos y Jesús Mora**.

Fuera del reloj:
- **Golossa** y **MSM** — fuera de roster desde el 09/09/2026 (Gerard): ya no trabajamos con
  estos clientes.
- **Midtown** — en pausa indefinida (ver `config/publicacion.json`). Cuando vuelva, se le da
  **desfase 3** y encaja sin tocar a nadie más.

## Añadir o quitar un cliente

Se toca **solo** `config/ciclo-mensual.json`:
- **Añadir**: una entrada en `desfase` con un número del 0 al 3. Elige el que esté libre para
  que no coincida su grabación con la de otro.
- **Quitar**: se borra su entrada (y se anota el porqué en `_fuera_del_reloj`).

## Lo que el reloj NO hace

No sustituye a los `manifest.json` de `ciclos/`, que siguen llevando el estado real de cada
etapa. El reloj dice **qué toca**; el manifest dice **cómo va**.
