from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.export_tasks",
        "app.tasks.scheduled_tasks",
    ],
)

celery_app.conf.task_routes = {
    "app.tasks.email_tasks.*": {"queue": "celery"},
    "app.tasks.export_tasks.*": {"queue": "celery"},
    "app.tasks.scheduled_tasks.*": {"queue": "celery"},
}

celery_app.conf.beat_schedule = {
    "generate-daily-report-every-minute": {
        "task": "daily_report",
        "schedule": crontab(hour=10, minute=30),
    },
}

celery_app.conf.timezone = "UTC"
