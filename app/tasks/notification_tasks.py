import json
import redis
from app.core.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="broadcast_notification")
def broadcast_notification_task(message: str):
    """
    Publishes a message to Redis with user_id='ALL'.
    This tells the API to broadcast it to everyone.
    """
    redis_url = (
        settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    )

    try:
        r = redis.from_url(redis_url, decode_responses=True)

        payload = {"user_id": "ALL", "message": message}

        r.publish("notifications", json.dumps(payload))
        return f"Broadcast Sent: {message}"

    except Exception as e:
        print(f"❌ Broadcast Failed: {e}")
        return f"Failed: {e}"
