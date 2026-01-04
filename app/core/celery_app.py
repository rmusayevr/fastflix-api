import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.email_tasks", "app.tasks.export_tasks"],
)

celery_app.conf.task_routes = {
    "app.tasks.email_tasks.*": {"queue": "celery"},
    "app.tasks.export_tasks.*": {"queue": "celery"},
}
