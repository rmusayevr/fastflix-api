from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.movie import MovieModel
from app.schemas.movie import MovieCreate, MovieUpdate


class MovieRepository:
    """
    Abstractions for database interactions.
    Wraps SQLAlchemy logic to decouple the Service layer from the ORM.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movie(self, movie_data: MovieCreate, user_id: int) -> MovieModel:
        """
        Create a new movie in the database.
        """
        movie = MovieModel(
            **movie_data.model_dump(),
            user_id=user_id,
        )

        self.session.add(movie)
        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    async def get_all_movies(self) -> list[MovieModel]:
        """
        Get all movies from the database.
        """
        query = select(MovieModel)

        result = await self.session.execute(query)

        return result.scalars().all()

    async def get_by_id(self, movie_id: int) -> MovieModel | None:
        """
        Get a movie by its ID.
        """
        query = select(MovieModel).where(MovieModel.id == movie_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_movie(
        self, movie: MovieModel, update_data: MovieUpdate
    ) -> MovieModel:
        """
        Update a movie in the database.
        """
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(movie, key, value)

        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    async def delete_movie(self, movie: MovieModel) -> None:
        """
        Delete a movie from the database.
        """
        await self.session.delete(movie)
        await self.session.commit()
