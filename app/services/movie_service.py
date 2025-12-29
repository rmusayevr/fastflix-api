from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.movie import MovieCreate
from app.models.movie import MovieModel
from app.schemas.movie import MovieUpdate
from app.repositories.movie_repository import MovieRepository


async def create_movie_service(movie: MovieCreate, db: AsyncSession) -> MovieModel:
    repo = MovieRepository(db)
    return await repo.create_movie(movie)


async def get_all_movies_service(db: AsyncSession) -> list[MovieModel]:
    repo = MovieRepository(db)
    return await repo.get_all_movies()


async def get_movie_by_id_service(movie_id: int, db: AsyncSession) -> MovieModel | None:
    repo = MovieRepository(db)
    return await repo.get_by_id(movie_id)


async def update_movie_service(
    movie_id: int, update_data: MovieUpdate, db: AsyncSession
) -> MovieModel | None:
    repo = MovieRepository(db)
    movie = await repo.get_by_id(movie_id)
    if not movie:
        return None

    return await repo.update_movie(movie, update_data)


async def delete_movie_service(movie_id: int, db: AsyncSession) -> bool:
    repo = MovieRepository(db)
    movie = await repo.get_by_id(movie_id)
    if not movie:
        return False

    await repo.delete_movie(movie)
    return True
