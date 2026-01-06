import asyncio
import random
import string
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import insert
from app.db.session import AsyncSessionLocal
from app.models.movie import Movie
from app.models.rating import RatingModel  # noqa: F401
from app.models.user import UserModel  # noqa: F401
from app.models.rbac import RoleModel  # noqa: F401
from app.models.watchlist import WatchlistModel  # noqa: F401
from app.models.notification import NotificationModel  # noqa: F401


def random_string(length=10):
    return "".join(random.choices(string.ascii_letters, k=length))


async def seed_large_db():
    print("🚀 Starting Bulk Seed (Target: 100,000 movies)...")
    start_time = time.time()

    batch_size = 5000
    total_records = 100000

    async with AsyncSessionLocal() as db:
        for i in range(0, total_records, batch_size):
            batch = []
            for _ in range(batch_size):
                title = f"Movie {random_string(5)}"
                batch.append(
                    {
                        "title": title,
                        "slug": f"{title}-{random_string(5)}",
                        "description": f"Description for {title}",
                        "release_year": random.randint(1990, 2025),
                        "video_url": "http://example.com",
                        "thumbnail_url": "http://example.com/img.jpg",
                        "average_rating": round(random.uniform(1.0, 10.0), 1),
                        "ratings_count": random.randint(0, 1000),
                    }
                )

            await db.execute(insert(Movie), batch)
            await db.commit()
            print(f"   - Inserted batch {i} to {i + batch_size}")

    duration = time.time() - start_time
    print(f"✅ Finished in {duration:.2f} seconds!")


if __name__ == "__main__":
    asyncio.run(seed_large_db())
