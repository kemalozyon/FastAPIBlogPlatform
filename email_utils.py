import logging
from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")


async def send_email(
        to_email : str,
        subject: str,
        plain_text : str,
        html_content: str | None = None
) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username or None,
        password=settings.mail_password.get_secret_value() or None,
        start_tls=settings.mail_use_tls,
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
KEMAL OZYON
"""

    try:
        await send_email(
            to_email=to_email,
            subject="Reset Your Password - FastAPI Blog",
            plain_text=plain_text,
            html_content=html_content,
        )
    except Exception:
        # Runs inside a BackgroundTask, so an unhandled error here would be
        # swallowed and never reach the client. Log it so failures are visible.
        logger.exception("Failed to send password reset email to %s", to_email)
        raise