from fastapi import APIRouter, Depends, status, Query, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slugify import slugify
from typing import Literal, List

from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.api.dependencies import get_db, get_current_user, get_current_admin
from app.models.user import UserModel
from app.models.movie import Movie, Genre
from app.services.movie_service import (
    get_all_movies_service,
    rate_movie_service,
    get_recommendations_service,
)
from app.schemas.common import PageResponse
from app.schemas.rating import RatingResponse, RatingCreate
from app.services.watchlist_service import toggle_watchlist_service

router = APIRouter()


@router.get(
    "/",
    response_model=PageResponse[MovieResponse],
    dependencies=[Depends(RateLimiter(times=50, seconds=60))],
)
async def read_movies(
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

    return fresh_movie


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
