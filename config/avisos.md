# Avisos — canales, cascada y plantillas

Todo aviso pasa por Winston, que llama al notificador (`infra/notifier/`). Regla de oro:
**solo se notifica lo accionable** (estado agregado + problemas). Nada de ruido por paso.

## Cascada de canales (en orden; cae al siguiente si falla)

1. **WhatsApp vía Evolution API** (PRIMARIO) — a tu propio número. Health check
   `connectionState = open` antes de enviar; si no está "open"/timeout → fallo → canal 2.
2. **Email** a `rmagency.proyectos@gmail.com` — fallback fiable; además el digest de ciclo
   y el cierre de mes van SIEMPRE por aquí.
3. **Push** al dispositivo — fallback de lo urgente.
4. **`INBOX-GERARD.md`** — se escribe SIEMPRE, pase lo que pase.

## Tipos de aviso

| Tipo | Cuándo | Canal | Urgencia |
|---|---|---|---|
| `DIGEST_CICLO` | Check-in diario de Winston | Email + INBOX | Normal |
| `CIERRE_MES` | Fin de ciclo, tras análisis | Email + WhatsApp + INBOX | Normal |
| `LOTE_LISTO` | Piezas pasan QA, listas para tu OK (Gate 2) | WhatsApp → … | Alta |
| `PROBLEMA` | Algo falla / bloqueo de QA / falta vídeo para un hueco / deadline 72h en riesgo | WhatsApp → … | Alta |
| `CANAL_WA_CAIDO` | Health check de WhatsApp falla | Email + push (no WhatsApp, obvio) | Alta |

## Plantillas (borrador — pulir con uso real)

**LOTE_LISTO**
```
🎬 Lote listo para tu OK — {cliente} · ciclo {ciclo}
{n} piezas pasaron QA. Revisa antes de enviar al cliente.
→ {ruta_ciclo}
```

**PROBLEMA**
```
⚠️ {cliente} · {tipo_problema}
{descripcion_corta}
Acción sugerida: {accion}
→ {ref}
```

**DIGEST_CICLO** (email)
```
Resumen semana {fecha} — RM Agency
Por cliente: {estado por etapa}
Bloqueos que requieren a Gerard: {lista}
Próximos deadlines (72h): {lista}
```
