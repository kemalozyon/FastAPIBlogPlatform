import logging

import boto3
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from config import settings

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")


def _get_ses_client():
    return boto3.client(
        "ses",
        region_name=settings.ses_region,
        aws_access_key_id=(settings.s3_access_key_id.get_secret_value() if settings.s3_access_key_id else None),
        aws_secret_access_key=(settings.s3_secret_access_key.get_secret_value() if settings.s3_secret_access_key else None),
    )


def _send_via_ses(
        to_email: str,
        subject: str,
        plain_text: str,
        html_content: str | None = None,
) -> None:
    ses = _get_ses_client()

    body: dict = {"Text": {"Data": plain_text, "Charset": "UTF-8"}}
    if html_content:
        body["Html"] = {"Data": html_content, "Charset": "UTF-8"}

    ses.send_email(
        Source=settings.mail_from,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": body,
        },
    )


async def send_email(
        to_email : str,
        subject: str,
        plain_text : str,
        html_content: str | None = None
) -> None:
    # boto3 is blocking, so hop to a threadpool to avoid stalling the event loop.
    await run_in_threadpool(
        _send_via_ses, to_email, subject, plain_text, html_content
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