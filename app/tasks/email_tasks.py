import asyncio
import logging
from pathlib import Path
from app.core.celery_app import celery_app
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_FOLDER = BASE_DIR / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email_to: str):
    """
    Celery task to send a welcome email using FastMail (Mailpit).
    """

    message = MessageSchema(
        subject="Welcome to FastFlix!",
        recipients=[email_to],
        body="<h1>Welcome to FastFlix!</h1><p>We are glad to have you.</p>",
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    try:
        asyncio.run(fm.send_message(message))
        logging.info(f"✅ Email sent to {email_to}")
        return f"Email sent to {email_to}"
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")
        raise e


@celery_app.task(name="send_reset_password_email")
def send_reset_password_email(email_to: str, token: str, username: str):
    import asyncio

    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
    template = env.get_template("reset_password.html")

    reset_link = f"{settings.DOMAIN}/reset-password?token={token}"
    html_content = template.render(username=username, link=reset_link, validity=15)
    message = MessageSchema(
        subject="FastFlix Password Recovery",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    loop = asyncio.get_event_loop()

    if loop.is_running():
        asyncio.create_task(fm.send_message(message))
    else:
        loop.run_until_complete(fm.send_message(message))

    logging.info(f"Reset email sent to {email_to}")
