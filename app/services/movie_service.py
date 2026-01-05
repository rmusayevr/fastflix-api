import json
import math

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from app.core.redis import get_redis_client
from app.repositories.movie_repository import MovieRepository
from app.schemas.common import PageResponse
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.models.movie import Movie
from app.schemas.rating import RatingCreate
from app.repositories.rating_repository import RatingRepository


async def invalidate_movie_cache():
    """Helper to clear all movie-related cache keys."""
    async with get_redis_client() as redis:
        keys = [key async for key in redis.scan_iter("movies:*")]
        if keys:
            await redis.delete(*keys)
            print(f"🧹 Invalidated {len(keys)} movie cache keys.")


async def get_all_movies_service(
    db: AsyncSession,
    page: int,
    size: int,
    search_query: str = None,
    sort_by: str = "id",
    order: str = "asc",
    min_rating: float = None,
) -> PageResponse[MovieResponse]:
    cache_key = f"movies:{page}:{size}:{search_query or 'all'}:{sort_by}:{order}:{min_rating or 'none'}"

    async with get_redis_client() as redis:
        cached_data = await redis.get(cache_key)
        if cached_data:
            print(f"⚡ Cache HIT for {cache_key}")
            return PageResponse(**json.loads(cached_data))

    repo = MovieRepository(db)
    skip = (page - 1) * size

    if search_query:
        items = await repo.search_movies(search_query)
        total = len(items)
    else:
        items, total = await repo.get_all_movies(
            skip=skip,
            limit=size,
            sort_by=sort_by,
            order=order,
            min_rating=min_rating,
            search_query=search_query,
        )

    items_data = [MovieResponse.model_validate(item) for item in items]
    total_pages = math.ceil(total / size) if size > 0 else 0

    response = PageResponse(
        items=items_data, total=total, page=page, size=size, pages=total_pages
    )

    async with get_redis_client() as redis:
        await redis.set(
            cache_key,
            json.dumps(jsonable_encoder(response)),
            ex=60,
        )
        print(f"🐢 Cache MISS for {cache_key} - Loaded from DB")

    return response


async def create_movie_service(
    movie: MovieCreate, user_id: int, db: AsyncSession
) -> Movie:
    repo = MovieRepository(db)
    new_movie = await repo.create_movie(movie, user_id)

    await invalidate_movie_cache()

    return new_movie


async def get_movie_by_id_service(movie_id: int, db: AsyncSession) -> Movie:
    repo = MovieRepository(db)
    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)
    return movie


async def update_movie_service(
    movie_id: int, update_data: MovieUpdate, user_id: int, db: AsyncSession
) -> Movie:
    repo = MovieRepository(db)

    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    if movie.user_id != user_id:
        raise NotAuthorizedException()

    updated_movie = await repo.update_movie(movie, update_data)

    await invalidate_movie_cache()

    return updated_movie


async def delete_movie_service(movie_id: int, user_id: int, db: AsyncSession) -> None:
    repo = MovieRepository(db)

    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    if movie.user_id != user_id:
        raise NotAuthorizedException()

    await repo.delete_movie(movie)

    await invalidate_movie_cache()


async def rate_movie_service(
    movie_id: int, rating_data: RatingCreate, user_id: int, db: AsyncSession
):
    movie_repo = MovieRepository(db)
    movie = await movie_repo.get_by_id(movie_id)
    if not movie:
        raise MovieNotFoundException(movie_id)

    rating_repo = RatingRepository(db)
    existing_rating = await rating_repo.get_rating(user_id, movie_id)

    if existing_rating:
        updated_rating = await rating_repo.update_rating(
            existing_rating, rating_data.score
        )
        return updated_rating
    else:
        new_rating = await rating_repo.create_rating(
            user_id, movie_id, rating_data.score
        )
        return new_rating


async def get_recommendations_service(movie_id: int, db: AsyncSession):
    repo = MovieRepository(db)
    movie = await repo.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return await repo.get_recommendations(movie_id)
