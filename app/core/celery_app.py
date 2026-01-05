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
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.task_routes = {
    "app.tasks.email_tasks.*": {"queue": "celery"},
    "app.tasks.export_tasks.*": {"queue": "celery"},
    "app.tasks.scheduled_tasks.*": {"queue": "celery"},
}

celery_app.conf.beat_schedule = {
    "refresh-trending-every-minute": {
        "task": "refresh_trending_cache",
        "schedule": crontab(day_of_week=1, hour=0, minute=0),
    },
}
celery_app.conf.timezone = "UTC"
