import redis.asyncio as redis
from app.core.config import settings

if settings.REDIS_URL:
    redis_pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True
    )
else:
    redis_pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        encoding="utf-8",
        decode_responses=True,
    )


def get_redis_client():
    """
    Returns a NEW client instance using the shared pool.
    This is crucial for Pub/Sub so we don't lock the main connection.
    """
    return redis.Redis(connection_pool=redis_pool)


async def get_redis():
    """Dependency for FastAPI routes"""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.close()
