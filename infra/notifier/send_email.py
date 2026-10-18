#!/usr/bin/env python3
"""Envía un email por SMTP (fallback del notificador cuando WhatsApp está caído).

Pensado para ejecutarse con /usr/bin/python3 (3.9), el único intérprete de este Mac que SÍ
tiene certificados SSL (python3.12 de brew falla contra TLS — ver memoria coste-tokens).

Config por variables de entorno (las pone notify.sh leyendo infra/.env):
  SMTP_HOST   (def. smtp.gmail.com)
  SMTP_PORT   (def. 465, SSL)
  SMTP_USER   remitente / usuario SMTP
  SMTP_PASS   contraseña de aplicación (Gmail: App Password de 16 caracteres, NO la normal)
  MAIL_TO     destinatario (EMAIL_DESTINO)
  MAIL_SUBJECT / MAIL_BODY

Sale 0 si se envió, 1 si faltan credenciales o falló el envío. No imprime el cuerpo.
"""
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage


def main():
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER", "").strip()
    # Gmail muestra la App Password en 4 grupos con espacios; el login la quiere sin espacios.
    pw = os.environ.get("SMTP_PASS", "").replace(" ", "").strip()
    to = os.environ.get("MAIL_TO", "")
    if not (user and pw and to):
        sys.stderr.write("Email sin configurar (faltan SMTP_USER/SMTP_PASS/MAIL_TO).\n")
        return 1

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = os.environ.get("MAIL_SUBJECT", "Aviso RM Agency")
    msg.set_content(os.environ.get("MAIL_BODY", ""))

    try:
        ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=20) as s:
                s.login(user, pw)
                s.send_message(msg)
        else:  # 587 STARTTLS
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.starttls(context=ctx)
                s.login(user, pw)
                s.send_message(msg)
        return 0
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"SMTP falló: {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
