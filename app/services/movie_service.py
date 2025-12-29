from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.movie import MovieCreate
from app.models.movie import MovieModel
from app.repositories.movie_repository import MovieRepository


async def create_movie_service(movie: MovieCreate, db: AsyncSession) -> MovieModel:
    repo = MovieRepository(db)
    return await repo.create_movie(movie)


async def get_all_movies_service(db: AsyncSession) -> list[MovieModel]:
    repo = MovieRepository(db)
    return await repo.get_all_movies()
