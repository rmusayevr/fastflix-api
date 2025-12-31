import redis.asyncio as redis
from app.core.config import settings

# Create a connection pool for Redis
redis_client = redis.from_url(
    settings.REDIS_URL, encoding="utf-8", decode_responses=True
)


async def get_redis():
    """Dependency to get Redis client"""
    return redis_client
