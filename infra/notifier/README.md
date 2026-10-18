# Notificador — cascada WhatsApp → email → push → INBOX

Módulo que usa Winston para avisar a Gerard. Intenta los canales en orden y cae al
siguiente si uno falla (ver `config/avisos.md` para tipos y plantillas).

## Contrato
`notify(tipo, mensaje, urgencia)`:
1. **WhatsApp (Evolution API)** — health check + `sendText`. Si falla → 2.
2. **Email** (`EMAIL_DESTINO`).
3. **Push** al dispositivo.
4. **INBOX** — anexa a `../../INBOX-GERARD.md` SIEMPRE.

## Health check + envío WhatsApp (referencia)
```bash
# Estado de la instancia (debe ser "open")
curl -s -H "apikey: $AUTHENTICATION_API_KEY" \
  http://127.0.0.1:8080/instance/connectionState/$WA_INSTANCE

# Enviar texto a ti mismo
curl -s -X POST -H "apikey: $AUTHENTICATION_API_KEY" -H "Content-Type: application/json" \
  http://127.0.0.1:8080/message/sendText/$WA_INSTANCE \
  -d "{\"number\":\"$WA_DESTINO\",\"text\":\"$MENSAJE\"}"
```
> Los endpoints/campos exactos dependen de la versión de Evolution API — verificar contra
> la doc de la versión fijada en `docker-compose.yml` antes de producción.

## Estado (actualizado 27/07/2026 — fallback cableado de verdad)
- ✅ `notify.sh` — WhatsApp + INBOX, y ahora **fallback real headless** (funciona en cron, sin agente).
- ✅ **Email (`send_email.py`)** — SMTP con `/usr/bin/python3` (el único con SSL). Se activa solo si
  hay `SMTP_USER` + `SMTP_PASS` (Gmail App Password) + `EMAIL_DESTINO` en `.env`. Si faltan, la
  cascada cae al push sin romper nada. (Sustituye al viejo "lo manda Winston por Gmail MCP", que
  solo funcionaba en sesión interactiva, no en el check-in por launchd.)
- ✅ **Push** — 1º notificación local de macOS (`osascript`, 0 credenciales); 2º opcional push al
  móvil vía `ntfy.sh` si defines `NTFY_TOPIC` en `.env` (te suscribes al topic en la app ntfy).

## Contrato de uso
```bash
infra/notifier/notify.sh "<mensaje>" <TIPO> <urgencia>
# Cascada: WhatsApp → email(SMTP) → push(macOS/ntfy) → INBOX(siempre).
# exit 0 → entregado por algún canal (además del INBOX). exit 1 → solo INBOX (todos caídos).
```
