# Transcripciones de las piezas de Xavi

Los archivos de Xavi no dicen de qué van (`Tanda 3-1.mp4`). Sin ver el vídeo no se puede
escribir el copy sin inventárselo, así que el 19/08/2026 se transcribieron con **AssemblyAI**
(`ASSEMBLYAI_API_KEY` ya estaba en `infra/.env`) las 12 piezas de septiembre.

`transcribir.py` acepta el **mp4 directo**, sin ffmpeg (que no está instalado en este Mac).
Cachea: si el `.txt` ya existe, no vuelve a gastar API. Coste ≈ céntimos por tanda.

```
/usr/bin/python3 transcribir.py "/Volumes/DD 2 TB WORK/Xavi Colomina/Acabats/TIPS ENTRENO/Tanda 3-5.mp4"
```

Para programar octubre en adelante, transcribe primero esa tanda y escribe los copies desde
`memoria/clientes/xavi-colomina/copy-brief.md`.

> Si esto resulta útil para más clientes, el sitio del script sería `infra/programacion/`.
> No se ha movido ahí sin el OK de Gerard (regla de Nova).

## Versiones alargadas (v2)

Cuando un corte se queda a mitad de frase se re-monta desde el master y se guarda al lado
como `..._v2.mp4`; la transcripción del corte nuevo se guarda como `<pieza>_v2.txt` (no se
pisa la vieja: el `.txt` original sigue documentando lo que se publicó/programó antes).
