import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.models.movie import Movie
from app.models.rating import RatingModel  # noqa: F401
from app.models.user import UserModel  # noqa: F401
from app.models.rbac import RoleModel  # noqa: F401
from app.models.watchlist import WatchlistModel  # noqa: F401
from app.models.notification import NotificationModel  # noqa: F401
from app.services.search_service import configure_search_index, add_movies_to_search


async def reindex():
    print("🔄 Starting Search Re-indexing...")

    await configure_search_index()

    async with AsyncSessionLocal() as db:
        stmt = select(Movie).options(selectinload(Movie.genres))
        result = await db.execute(stmt)
        movies = result.scalars().all()

        print(f"📦 Fetched {len(movies)} movies from Database.")

        if movies:
            await add_movies_to_search(movies)
        else:
            print("⚠️ No movies found in DB to sync.")

    print("✅ Re-indexing complete!")


if __name__ == "__main__":
    asyncio.run(reindex())
