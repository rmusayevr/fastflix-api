from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.watchlist import WatchlistModel
from app.models.movie import Movie
from sqlalchemy import desc


class WatchlistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_item(self, user_id: int, movie_id: int) -> WatchlistModel | None:
        """Check if a movie is already in the user's watchlist."""
        query = select(WatchlistModel).where(
            WatchlistModel.user_id == user_id, WatchlistModel.movie_id == movie_id
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def add_item(self, user_id: int, movie_id: int) -> WatchlistModel:
        item = WatchlistModel(user_id=user_id, movie_id=movie_id)
        self.session.add(item)
        await self.session.commit()
        return item

    async def remove_item(self, user_id: int, movie_id: int):
        query = delete(WatchlistModel).where(
            WatchlistModel.user_id == user_id, WatchlistModel.movie_id == movie_id
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_user_watchlist(self, user_id: int, skip: int, limit: int):
        """
        Get all movies in the user's watchlist, ordered by most recently added.
        """
        query = (
            select(Movie)
            .join(WatchlistModel, Movie.id == WatchlistModel.movie_id)
            .where(WatchlistModel.user_id == user_id)
            .order_by(desc(WatchlistModel.added_at))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
