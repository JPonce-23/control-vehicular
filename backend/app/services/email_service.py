"""
Servicio temporalmente deshabilitado.

La empresa no cuenta actualmente con infraestructura de correo
para recuperación de contraseñas.

Se conserva para futura implementación de SMTP corporativo.
"""

import os
import smtplib
from email.message import EmailMessage

def enviar_correo_recuperacion(destinatario: str, token: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM")

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recuperación de contraseña"
    mensaje["From"] = smtp_from
    mensaje["To"] = destinatario

    mensaje.set_content(
        f"""
Hola.

Tu código de recuperación es:

{token}

Este código vence en 5 minutos.

Si no solicitaste este cambio, ignora este correo.
"""
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(mensaje)