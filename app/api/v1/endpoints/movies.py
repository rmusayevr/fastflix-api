import json
from slugify import slugify
from typing import Literal, List
from fastapi import APIRouter, Depends, status, Query, HTTPException, Request

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db, get_current_user, get_current_admin
from app.core.limiter import limiter
from app.core.redis import get_redis_client
from app.models.user import UserModel
from app.models.movie import Movie, Genre
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.services.movie_service import (
    get_all_movies_service,
    rate_movie_service,
    get_recommendations_service,
)
from app.schemas.common import PageResponse
from app.schemas.rating import RatingResponse, RatingCreate
from app.services.watchlist_service import toggle_watchlist_service
from app.tasks.notification_tasks import broadcast_notification_task

router = APIRouter()


@router.get(
    "/",
    response_model=PageResponse[MovieResponse],
)
@limiter.limit("10/minute")
async def read_movies(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: Literal["id", "title", "rating"] = "rating",
    order: Literal["asc", "desc"] = "desc",
    min_rating: float = Query(
        None, ge=0, le=10, description="Filter movies with avg rating >= this value"
    ),
    search_query: str = Query(
        None, description="Search movies by title or description"
    ),
):
    return await get_all_movies_service(
        db,
        page,
        size,
        search_query=search_query,
        sort_by=sort_by,
        order=order,
        min_rating=min_rating,
    )


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_in: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    slug = slugify(movie_in.title)

    new_movie = Movie(
        title=movie_in.title,
        slug=slug,
        description=movie_in.description,
        release_year=movie_in.release_year,
        video_url=movie_in.video_url,
        thumbnail_url=movie_in.thumbnail_url,
    )

    if movie_in.genre_ids:
        stmt = select(Genre).where(Genre.id.in_(movie_in.genre_ids))
        result = await db.execute(stmt)
        genres = result.scalars().all()

        if len(genres) != len(movie_in.genre_ids):
            raise HTTPException(
                status_code=404, detail="One or more Genre IDs not found"
            )

        new_movie.genres = list(genres)

    db.add(new_movie)
    await db.commit()
    stmt = (
        select(Movie)
        .options(selectinload(Movie.genres))
        .where(Movie.id == new_movie.id)
    )
    result = await db.execute(stmt)
    fresh_movie = result.scalars().first()

    broadcast_notification_task.delay(f"🎬 New Release: {fresh_movie.title}")

    return fresh_movie


@router.get("/trending", response_model=list[MovieResponse])
@limiter.limit("5/minute")
async def get_trending_movies(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Fetches the Top 5 Trending movies from the Redis Cache.
    If cache is empty (e.g. first run), falls back to DB or returns empty.
    Rate Limit: 5 per minute per IP.
    """
    redis = get_redis_client()
    cached_data = await redis.get("trending_movies")

    movie_ids = []

    if cached_data:
        data = json.loads(cached_data)
        movie_ids = data.get("movie_ids", [])
        print(f"⚡ Cache Hit! Serving IDs: {movie_ids}")
    else:
        print("⚠️ Cache Miss! (Worker hasn't run yet)")
        return []

    if movie_ids:
        stmt = (
            select(Movie)
            .options(selectinload(Movie.genres))
            .where(Movie.id.in_(movie_ids))
        )
        result = await db.execute(stmt)
        movies = result.scalars().all()

        movies_map = {m.id: m for m in movies}
        ordered_movies = [movies_map[mid] for mid in movie_ids if mid in movies_map]

        return ordered_movies

    return []


@router.get("/{movie_id}", response_model=MovieResponse)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@router.patch("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    stmt = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    update_data = movie_in.model_dump(exclude_unset=True)

    genre_ids = update_data.pop("genre_ids", None)

    for field, value in update_data.items():
        setattr(movie, field, value)

    if genre_ids is not None:
        stmt_genres = select(Genre).where(Genre.id.in_(genre_ids))
        genres_result = await db.execute(stmt_genres)
        new_genres = genres_result.scalars().all()

        movie.genres = list(new_genres)

    await db.commit()
    await db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    await db.delete(movie)
    await db.commit()
    return None


@router.post("/{movie_id}/rate", response_model=RatingResponse)
async def rate_movie(
    movie_id: int,
    rating_data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await rate_movie_service(movie_id, rating_data, current_user.id, db)


@router.post("/{movie_id}/watchlist")
async def toggle_watchlist(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await toggle_watchlist_service(current_user.id, movie_id, db)


@router.get("/{movie_id}/recommendations", response_model=List[MovieResponse])
async def get_movie_recommendations(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get 5 recommended movies based on user viewing patterns.
    """
    return await get_recommendations_service(movie_id, db)
