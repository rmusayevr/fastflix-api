import json
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from app.core.redis import redis_client
from app.repositories.movie_repository import MovieRepository
from app.schemas.common import PageResponse
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.models.movie import MovieModel


async def get_all_movies_service(
    db: AsyncSession, page: int, size: int, search_query: str | None = None
) -> PageResponse[MovieResponse]:
    cache_key = f"movies:{page}:{size}:{search_query or 'all'}"

    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print(f"⚡ Cache HIT for {cache_key}")
        return PageResponse(**json.loads(cached_data))

    repo = MovieRepository(db)
    skip = (page - 1) * size

    if search_query:
        items = await repo.search_movies(search_query)
        total = len(items)
    else:
        items, total = await repo.get_all_movies(skip=skip, limit=size)
        
    items_data = [MovieResponse.model_validate(item) for item in items]

    import math

    total_pages = math.ceil(total / size) if size > 0 else 0

    response = PageResponse(
        items=items_data, total=total, page=page, size=size, pages=total_pages
    )

    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(response)),
        ex=60,
    )

    print(f"🐢 Cache MISS for {cache_key} - Loaded from DB")
    return response


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
