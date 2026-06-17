import httpx
from fastapi.templating import Jinja2Templates

from config import settings

templates = Jinja2Templates(directory="templates")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


async def send_email(
        to_email : str,
        subject: str,
        plain_text : str,
        html_content: str | None = None
) -> None:
    payload: dict = {
        "sender": {"email": settings.mail_from},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": plain_text,
    }
    if html_content:
        payload["htmlContent"] = html_content

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            BREVO_API_URL,
            headers={
                "api-key": settings.brevo_api_key.get_secret_value(),
                "accept": "application/json",
                "content-type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()


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

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )