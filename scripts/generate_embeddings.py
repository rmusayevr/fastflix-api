import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.movie import Movie
from app.models.rating import RatingModel  # noqa: F401
from app.models.user import UserModel  # noqa: F401
from app.models.rbac import RoleModel  # noqa: F401
from app.models.watchlist import WatchlistModel  # noqa: F401
from app.models.notification import NotificationModel  # noqa: F401
from app.services.ai_service import get_embedding


async def generate_embeddings():
    print("🚀 Starting AI Embedding Generation...")

    batch_size = 100
    total_processed = 0

    async with AsyncSessionLocal() as db:
        while True:
            stmt = select(Movie).where(Movie.embedding.is_(None)).limit(batch_size)
            result = await db.execute(stmt)
            movies = result.scalars().all()

            if not movies:
                break

            print(f"🧠 Processing batch of {len(movies)} movies...")

            for movie in movies:
                text_to_embed = f"{movie.title}: {movie.description}"

                vector = get_embedding(text_to_embed)

                movie.embedding = vector

            await db.commit()
            total_processed += len(movies)
            print(f"✅ Saved {total_processed} vectors so far.")

    print("🎉 All movies have been embedded!")


if __name__ == "__main__":
    asyncio.run(generate_embeddings())
