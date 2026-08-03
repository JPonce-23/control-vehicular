import smtplib
from email.message import EmailMessage

from app.config import get_settings


def smtp_configurado() -> bool:
    settings = get_settings()
    return all(
        [
            settings.smtp_host,
            settings.smtp_user,
            settings.smtp_password,
            settings.smtp_from,
        ]
    )


def enviar_correo_recuperacion(destinatario: str, token: str) -> None:
    settings = get_settings()
    if not smtp_configurado():
        raise RuntimeError("El servicio de correo no está configurado")

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recuperación de contraseña"
    mensaje["From"] = settings.smtp_from
    mensaje["To"] = destinatario
    mensaje.set_content(
        f"Hola.\n\nTu código de recuperación es:\n\n{token}\n\n"
        "Este código vence en 5 minutos.\n\n"
        "Si no solicitaste este cambio, ignora este correo."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(mensaje)
