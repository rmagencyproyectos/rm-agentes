# Biblioteca de sonidos de Gerard (fase 3)

Origen: proyecto de CapCut «RM Dia de trabajo», **Clip combinado16** (en 1:48), revisado el 03/11/2026.
Orden: por momento de inicio dentro del clip combinado y, si empiezan a la vez, por pista (de arriba abajo).
Gerard entrega los archivos por separado **en este orden** (01, 02…); al llegar se nombran `gNN_<categoria>.<ext>`.

| Nº | Nombre en CapCut | Categoría | Duración | Para qué |
|---|---|---|---|---|
| 01 | click (camera shutter sound single shot) | obturador | 0.30 s | foto / «mira esto» / congelar un momento |
| 02 | 转场 C10 (transición C10) | transicion | 0.80 s | cambio de plano, transición |
| 03 | Wind noise used by Youtuber | whoosh | 1.00 s | whoosh de aire: entrada de titular grande o cambio de plano |
| 04 | Tick tock second hand of the clock | reloj | 159.27 s | tiempo / esperar / «rápido» (se recorta al usarlo) |
| 05 | Finger patchon (finger snap E) | chasquido | 0.47 s | «así de fácil», cambio instantáneo, aparece algo |
| 06 | Cut the wind Hew somewhat lower | whoosh_corto | 0.47 s | whoosh corto: entrada rápida, swipe |
| 07 | Culin. Light bulb mark | idea | 1.30 s | idea / truco / «tip» (bombilla) |
| 08 | Computer-Mouse-Click_PREM11-1148 | click | 1.00 s | clic: «guardar», botón, seleccionar |
| 09 | Dokudoku tension tense heart beat | tension | 13.67 s | tensión / suspense antes de revelar (se recorta) |
| 10 | Beep (short) | beep | 0.70 s | aviso / censura / error leve |
| 11 | Pencil write circle add circle | dibujar | 0.53 s | rodear / subrayar / marcar algo en pantalla |
| 12 | Crickets in the countryside | grillos | 900.00 s | silencio incómodo / humor (se recorta) |
| 13 | Money, coin, cash register | dinero | 0.90 s | precio / ahorro / dinero |
| 14 | Champagne Pop | pop | 1.03 s | celebración / resultado / entrada con fuerza |
| 15 | Sundon: Impact sound | impacto | 6.47 s | exclamación / golpe de efecto (con cola) |
| 16 | 转场 E14 (transición E14) | transicion_corta | 0.43 s | transición rápida |
| 17 | Bell ring «ding!» | ding | 1.77 s | acierto / visto bueno / dato bueno |
| 18 | RISER_01 | riser | 4.10 s | subida antes de algo importante / CTA |
| 19 | pop! (tapping the mouth with a hand) | pop_suave | 0.37 s | entrada de titular / elemento (pop de boca) |

## Para cortar el archivo que exporta Gerard

Proyecto de CapCut **«Biblioteca sonidos RM»** (03/11): los 19 en una sola pista, en este orden, con **0.5 s de
silencio** entre uno y otro. Grillos recortados a 6 s y reloj a 10 s (en el clip combinado estaban enteros); el
resto entero. Total 1:00.01 (60.014 s). Exportar el audio entero desde 0:00 y cortarlo con
`python3 precapcut.py sonidos-cortar <archivo>` (usa estos tiempos y comprueba que los cortes caen en silencio).

| Nº | Empieza | Acaba |
|---|---|---|
| 01 | 0:00.00 (0.0 s) | 0:00.29 (0.293 s) |
| 02 | 0:00.79 (0.793 s) | 0:01.56 (1.559 s) |
| 03 | 0:02.06 (2.059 s) | 0:03.06 (3.057 s) |
| 04 | 0:03.56 (3.557 s) | 0:13.56 (13.557 s) |
| 05 | 0:14.06 (14.057 s) | 0:14.50 (14.499 s) |
| 06 | 0:15.00 (14.999 s) | 0:15.44 (15.441 s) |
| 07 | 0:15.94 (15.941 s) | 0:17.22 (17.219 s) |
| 08 | 0:17.72 (17.719 s) | 0:18.70 (18.704 s) |
| 09 | 0:19.20 (19.204 s) | 0:32.86 (32.864 s) |
| 10 | 0:33.36 (33.364 s) | 0:34.05 (34.045 s) |
| 11 | 0:34.55 (34.545 s) | 0:35.07 (35.071 s) |
| 12 | 0:35.57 (35.571 s) | 0:41.57 (41.571 s) |
| 13 | 0:42.07 (42.071 s) | 0:42.96 (42.957 s) |
| 14 | 0:43.46 (43.457 s) | 0:44.47 (44.474 s) |
| 15 | 0:44.97 (44.974 s) | 0:51.42 (51.424 s) |
| 16 | 0:51.92 (51.924 s) | 0:52.33 (52.33 s) |
| 17 | 0:52.83 (52.83 s) | 0:54.58 (54.578 s) |
| 18 | 0:55.08 (55.078 s) | 0:59.15 (59.151 s) |
| 19 | 0:59.65 (59.651 s) | 1:00.01 (60.014 s) |
