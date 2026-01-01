import time
from app.core.celery_app import celery_app


@celery_app.task
def send_welcome_email(email: str):
    """
    Simulates sending a welcome email.
    """
    print(f"📧 [START] Preparing email for {email}...")

    time.sleep(5)

    print(f"✅ [SENT] Welcome email sent to {email}!")
    return f"Email sent to {email}"
