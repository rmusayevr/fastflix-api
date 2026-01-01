import redis.asyncio as redis
from app.core.config import settings

if settings.REDIS_URL:
    redis_client = redis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True
    )
else:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding="utf-8",
        decode_responses=True,
    )


async def get_redis():
    """Dependency to get Redis client"""
    return redis_client
