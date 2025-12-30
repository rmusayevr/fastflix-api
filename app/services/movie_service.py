from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.movie import MovieModel
from app.schemas.movie import MovieCreate, MovieUpdate
from app.repositories.movie_repository import MovieRepository
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException


async def create_movie_service(
    movie: MovieCreate, user_id: int, db: AsyncSession
) -> MovieModel:
    repo = MovieRepository(db)
    return await repo.create_movie(movie, user_id)


async def get_all_movies_service(db: AsyncSession) -> List[MovieModel]:
    repo = MovieRepository(db)
    return await repo.get_all_movies()


async def get_movie_by_id_service(movie_id: int, db: AsyncSession) -> MovieModel:
    repo = MovieRepository(db)
    movie = await repo.get_by_id(movie_id)

    if not movie:
        raise MovieNotFoundException(movie_id)

    return movie


async def update_movie_service(
    movie_id: int, update_data: MovieUpdate, user_id: int, db: AsyncSession
) -> MovieModel:
    repo = MovieRepository(db)

    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    if movie.user_id != user_id:
        raise NotAuthorizedException()

    return await repo.update_movie(movie, update_data)


async def delete_movie_service(movie_id: int, user_id: int, db: AsyncSession) -> None:
    repo = MovieRepository(db)

    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    if movie.user_id != user_id:
        raise NotAuthorizedException()

    await repo.delete_movie(movie)
