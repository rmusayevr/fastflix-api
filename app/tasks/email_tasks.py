import logging
from app.core.celery_app import celery_app
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER or "",
    MAIL_PASSWORD=settings.SMTP_PASSWORD or "",
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False,
)


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email_to: str):
    """
    Celery task to send a welcome email.
    Note: We must use sync wrapper or run async code properly.
    FastMail is async, but Celery is traditionally sync.
    We will use 'async_to_sync' or just standard python blocking for simplicity if needed,
    but FastMail is designed for async.

    Workaround: We run the async sending function inside a sync loop.
    """
    import asyncio

    message = MessageSchema(
        subject="Welcome to FastFlix!",
        recipients=[email_to],
        body="<h1>Welcome to FastFlix!</h1><p>We are glad to have you.</p>",
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(fm.send_message(message))
    else:
        loop.run_until_complete(fm.send_message(message))

    logging.info(f"Email sent to {email_to}")
    return f"Email sent to {email_to}"
