import json
import redis
import asyncio
from sqlalchemy import select, func
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import AsyncSessionLocal, engine
from app.models.movie import Movie


@celery_app.task(name="refresh_trending_cache")
def refresh_trending_cache_task():
    """
    Real Logic: Fetches 5 random EXISTING IDs from the database using AsyncIO.
    """
    print("🔄 [START] Calculating Trending Movies...")

    async def fetch_trending_ids():
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(Movie.id).order_by(func.random()).limit(5)
                result = await session.execute(stmt)
                data = result.scalars().all()
                return data
        finally:
            await engine.dispose()

    try:
        trending_ids = asyncio.run(fetch_trending_ids())

        if not trending_ids:
            print("⚠️ No movies found in DB to cache.")
            return "No Data"

        payload = {
            "source": "celery_beat",
            "movie_ids": list(trending_ids),
            "algorithm": "random_db_sample",
        }

        redis_url = (
            settings.REDIS_URL
            or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
        )
        r = redis.from_url(redis_url, decode_responses=True)
        r.set("trending_movies", json.dumps(payload), ex=3600)

        print(f"✅ [DONE] Trending Cache Updated with REAL IDs: {trending_ids}")
        return f"Cache Updated: {trending_ids}"

    except Exception as e:
        print(f"❌ Cache Update Failed: {e}")
        return f"Failed: {e}"
