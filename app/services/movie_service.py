import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.models.movie import MovieModel
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from app.core.redis import redis_client


async def get_all_movies_service(db: AsyncSession) -> List[MovieResponse]:
    cache_key = "all_movies_list"

    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            print("🚀 CACHE HIT: Returning movies from Redis")
            return json.loads(cached_data)
    except Exception as e:
        print(f"⚠️ Redis Error: {e}")

    print("🐢 CACHE MISS: Fetching from PostgreSQL")
    repo = MovieRepository(db)
    movies = await repo.get_all_movies()

    movie_list = []
    for m in movies:
        movie_dict = {
            "id": m.id,
            "title": m.title,
            "director": m.director,
            "description": m.description,
            "user_id": m.user_id,
        }
        movie_list.append(movie_dict)

    try:
        await redis_client.setex(cache_key, 60, json.dumps(movie_list))
    except Exception as e:
        print(f"⚠️ Failed to cache data: {e}")

    return movies


async def create_movie_service(
    movie: MovieCreate, user_id: int, db: AsyncSession
) -> MovieModel:
    repo = MovieRepository(db)
    new_movie = await repo.create_movie(movie, user_id)

    print("🧹 Invalidating Cache: all_movies_list")
    await redis_client.delete("all_movies_list")

    return new_movie


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

    updated_movie = await repo.update_movie(movie, update_data)

    print("🧹 Invalidating Cache: all_movies_list")
    await redis_client.delete("all_movies_list")

    return updated_movie


async def delete_movie_service(movie_id: int, user_id: int, db: AsyncSession) -> None:
    repo = MovieRepository(db)

    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    if movie.user_id != user_id:
        raise NotAuthorizedException()

    await repo.delete_movie(movie)

    print("🧹 Invalidating Cache: all_movies_list")
    await redis_client.delete("all_movies_list")
