"""Genera metricool.json de octubre 2026 (Xavi) desde los copies escritos aquí.

Fechas, piezas y vídeos: los de la base de Notion «Contenido Xavi Colomina» (Publicación,
Vídeo final), que es la fuente viva. El videos.json de septiembre tenía otro orden a partir
del 20/10 y no incluía la Tanda 3-7.
Copies: escritos el 23/09/2026 desde las transcripciones (../transcripciones) y el
copy-brief. Regla de Gerard: sin CTA, 25-50 palabras, la mentalidad al final.
"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
H = "15:00"
P = [
 ("2026-10-06","Tanda 3-5","3c1496ca6d51815994d0ebca9ccf1d1a","1_829XniT4C5FUTDvzcJr3lsxBsfhmsIi",
  "Si decides mientras la bola flota, ya decides tarde.\n\n¿Cuándo tomar la decisión en pádel?\n\nMientras la bola está en el aire, solo toca ganar tiempo y espacio. La elección llega al golpear. El que piensa antes se queda quieto; el que confía en su lectura, se mueve.\n\n#Padel #TacticaDePadel #TomaDeDecisiones #TecnicaDePadel #EntrenamientoDePadel #PadelTips #CoachDePadel #PadelAmateur",
  "Decides tarde y por eso llegas tarde | Toma de decisiones en pádel"),
 ("2026-10-08","C04 — La relación contigo mismo","3c1496ca6d5181ec920fdbccc0e40523","10_H3pzmGRnSjz1VmJ2mLMc8yMRudjVKU",
  "Cómo juegas al pádel dice mucho de cómo te tratas.\n\n¿Qué tiene que ver la paciencia con tu juego en pista?\n\nEl que no se da tregua a sí mismo tampoco se la da entre punto y punto. Por eso la #MentalidadDeportiva empieza por mirarte a ti antes que al resultado.\n\n#Padel #PsicologiaDeportiva #MentalidadPadel #CoachDePadel #EntrenadorDePadel #PadelTips #PadelAmateur #Competicion",
  "Tu pádel refleja cómo te tratas a ti mismo | Mentalidad en pádel"),
 ("2026-10-11","Evitar ángulos","3c1496ca6d5181989335d7c889a4d60c","1fbyizz2X0HjpLOY7hPvi4_TOWACUb5q8",
  "Abrir un ángulo pronto es regalarle otro al rival.\n\n¿Cómo atacar en pádel sin que te contraataquen?\n\nPrimero cuerpo y profundidad, hasta que tenga que girarse y le quede la bola alta. Luego cambias. El ángulo es el premio del punto, no el atajo: hay que tener paciencia para ganárselo.\n\n#Padel #TacticaDePadel #AtaqueEnPadel #TecnicaDePadel #EntrenamientoDePadel #PosicionEnPista #PadelTips #CoachDePadel #PadelAmateur",
  "No abras ángulos pronto: ataca al cuerpo | Táctica de pádel"),
 ("2026-10-13","Ejercicio 2","3c1496ca6d5181fb9309f0098c42db2c","1b8UPSyo631cMZaM0uRrl_NxuuX_QJaq9",
  "El ejercicio que más odian sus alumnos es el que más los hace mejorar.\n\n¿Para qué sirve subir y bajar en un entrenamiento de pádel?\n\nTe obliga a medir velocidades, recuperar espacio y llegar alineado para cargar el peso delante. Es exigente a propósito: el criterio se construye cuando cansa.\n\n#Padel #EjerciciosDePadel #EntrenamientoDePadel #TecnicaDePadel #PosicionEnPista #PadelTips #CoachDePadel #PadelAmateur",
  "Ejercicio de pádel de subir y bajar: por qué todos lo odian"),
 ("2026-10-15","Tanda 3-6","3c1496ca6d518121aec4dd2919fb663a","1dBjpLlifrdKsk63Uw2v9wa4uPtoYLntu",
  "Hoy todo el mundo defiende. Lo que no aguanta nadie es quedarse sin tiempo.\n\n¿Cómo incomodar al rival en pádel?\n\nUn buen golpe no basta si le das tiempo a recolocarse. Pensar en su tiempo y no en tu golpe es lo que cambia el partido.\n\n#Padel #TacticaDePadel #GestionDelTiempo #TecnicaDePadel #EntrenamientoDePadel #PadelTips #CoachDePadel #PadelAmateur",
  "Si le quitas el tiempo, se lo quitas todo | Táctica de pádel"),
 ("2026-10-18","Fallo de movimiento","3c1496ca6d51811494e9c9350b10dfe9","1BNuNUSiEFgZwjSvs7pFgblLZTHVk7jnS",
  "Esperar la bola es cederle metros al rival.\n\n¿Por qué te comen terreno en pádel?\n\nSi esperas y te vas al lateral, la pista es suya. Anticípate y ve hacia delante. Moverse antes no es cuestión de piernas: es decidir que ese espacio es tuyo.\n\n#Padel #MovimientoEnPista #PosicionEnPista #TecnicaDePadel #EntrenamientoDePadel #PadelTips #CoachDePadel #PadelAmateur",
  "Si esperas la bola te comen terreno | Movimiento en pádel"),
 ("2026-10-20","Tanda 3-7","3c1496ca6d51818e9eafd61592bc4bfd","1T7uYrby8m0E54VZL-6ln3XwhUuIQ0SXu",
  "Camina, golpea y vuelve. Casi todo el mundo se salta un paso.\n\n¿Cómo cargar el peso en el golpeo de pádel?\n\nUn paso y cargas. Y volver también es parte del golpe: el punto no acaba cuando la bola sale de tu pala.\n\n#Padel #GolpeoEnPadel #TecnicaDePadel #EntrenamientoDePadel #MovimientoEnPista #PadelTips #CoachDePadel #PadelAmateur",
  "Camina, golpea y vuelve | Golpeo en pádel"),
 ("2026-10-22","C07 — Crítica, ego y estrella","3c1496ca6d518169b5e5f5041ba94061","184GY_qfSMZIk3fXk0UzOkUlwrf658NYN",
  "El ego también juega. Y casi siempre en contra de tu pareja.\n\n¿Qué pasa cuando uno quiere todo el protagonismo en pádel?\n\nUna volea espectacular que no te tocaba descoloca a la pareja y te pasa del ataque a la defensa. En pádel se gana en pareja.\n\n#Padel #MentalidadDeportiva #PsicologiaDeportiva #MentalidadPadel #TacticaDePadel #CoachDePadel #PadelTips #PadelPro",
  "El ego en el pádel: cuando la volea espectacular te hace perder"),
 ("2026-10-25","Flash tip 1","3c1496ca6d5181c2b8f9eed04d7dae0b","14emPhVhDG07ayVSpv7LPImxC1WijnTxV",
  "Esperar a que la bola baje es regalar altura.\n\n¿A qué altura golpear la bola en pádel?\n\nLo más arriba posible dentro de su caída. Cada centímetro que esperas es tiempo que le das al rival. Ir a buscarla arriba es una decisión antes que un gesto.\n\n#Padel #GolpeoEnPadel #TecnicaDePadel #EntrenamientoDePadel #PuntoDeImpacto #PadelTips #CoachDePadel #PadelAmateur",
  "Golpea la bola lo más arriba posible | Técnica de pádel"),
 ("2026-10-27","Tanda 3-8","3c1496ca6d5181cdad62f0a42d62d45e","1Lvgims47YfnPiHGwTdNJPBRQB7K7T-nk",
  "Correr más no te sube de nivel.\n\n¿Qué marca de verdad el nivel de un jugador de pádel?\n\nTodo empieza en la lectura: si lees antes, te colocas y tienes tiempo para elegir. El que corre a todas ha leído tarde. Leer primero es una forma de pensar.\n\n#Padel #NivelDePadel #TecnicaDePadel #EntrenamientoDePadel #CentroDeGravedad #PadelTips #CoachDePadel #PadelAmateur",
  "Las 3 cosas que marcan tu nivel de pádel (y no es correr)"),
 ("2026-10-29","Flash tip 2","3c1496ca6d5181069fa5ce1df1049430","1YmGlzypVIEtM69rv8R6sUTfIiWe8KAn2",
  "Armar en parado es llegar tarde con la pala preparada.\n\n¿Cuándo armar el golpe en pádel?\n\nEn movimiento, mientras te desplazas. El que se para a preparar está reaccionando; el que arma andando ya está decidiendo.\n\n#Padel #GolpeoEnPadel #PreparacionDelGolpe #TecnicaDePadel #EntrenamientoDePadel #PadelTips #CoachDePadel #PadelAmateur",
  "Arma el golpe en movimiento, no en parado | Técnica de pádel"),
]
# C04 fuera (25/09): Gerard dice que lo subió él a mano; no está en el planner ni en Drive.
FUERA = {"C04 — La relación contigo mismo"}
posts = [{"fecha": f, "hora": H, "titulo": t, "notion_id": nid, "redes": ["instagram", "tiktok", "youtube"],
          "cliente": "xavi-colomina", "brand_id": 6276334, "drive_id": d, "texto": c, "yt_titulo": y}
         for f, t, nid, d, c, y in P if t not in FUERA]
json.dump({"cliente": "xavi-colomina", "generado": "2026-09-23", "posts": posts},
          open(os.path.join(AQUI, "metricool.json"), "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    import re
    for p in posts:
        cuerpo = re.sub(r"#\w+", "", p["texto"].rsplit("\n\n", 1)[0])
        tags = re.findall(r"#(\w+)", p["texto"])
        dup = len(tags) != len({x.lower() for x in tags})
        print(p["fecha"], f"{len(cuerpo.split())} palabras", f"{len(tags)} hashtags", "DUP!" if dup else "", f"YT {len(p['yt_titulo'])} car.", "| " + p["titulo"])
