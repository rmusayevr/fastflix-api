from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.movie_repository import MovieRepository
from fastapi import HTTPException


async def toggle_watchlist_service(user_id: int, movie_id: int, db: AsyncSession):
    movie_repo = MovieRepository(db)
    movie = await movie_repo.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    watchlist_repo = WatchlistRepository(db)
    existing_item = await watchlist_repo.get_item(user_id, movie_id)

    if existing_item:
        await watchlist_repo.remove_item(user_id, movie_id)
        return {"status": "removed", "movie_id": movie_id}
    else:
        await watchlist_repo.add_item(user_id, movie_id)
        return {"status": "added", "movie_id": movie_id}


async def get_user_watchlist_service(
    user_id: int, page: int, size: int, db: AsyncSession
):
    repo = WatchlistRepository(db)
    movies = await repo.get_user_watchlist(user_id, skip=(page - 1) * size, limit=size)
    return movies
