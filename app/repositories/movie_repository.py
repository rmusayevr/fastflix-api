from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.movie import MovieModel
from app.schemas.movie import MovieCreate


class MovieRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movie(self, movie_data: MovieCreate) -> MovieModel:
        movie = MovieModel(**movie_data.model_dump())

        self.session.add(movie)
        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    async def get_all_movies(self) -> list[MovieModel]:
        query = select(MovieModel)

        result = await self.session.execute(query)

        return result.scalars().all()
