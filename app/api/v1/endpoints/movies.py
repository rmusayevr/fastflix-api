from fastapi import APIRouter, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal

from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.api.dependencies import get_db, get_current_user
from app.models.user import UserModel
from app.services.movie_service import (
    create_movie_service,
    get_all_movies_service,
    get_movie_by_id_service,
    update_movie_service,
    delete_movie_service,
    rate_movie_service,
)
from app.schemas.common import PageResponse
from app.schemas.rating import RatingResponse, RatingCreate

router = APIRouter()


@router.get(
    "/",
    response_model=PageResponse[MovieResponse],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_movies(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: Literal["id", "title", "rating"] = "rating",
    order: Literal["asc", "desc"] = "desc",
):
    return await get_all_movies_service(
        db, page, size, search_query=q, sort_by=sort_by, order=order
    )


@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(
    movie: MovieCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_movie_service(movie, current_user.id, db)


@router.get("/{movie_id}", response_model=MovieResponse)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await get_movie_by_id_service(movie_id, db)


@router.patch("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await update_movie_service(movie_id, movie_in, current_user.id, db)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    await delete_movie_service(movie_id, current_user.id, db)


@router.post("/{movie_id}/rate", response_model=RatingResponse)
async def rate_movie(
    movie_id: int,
    rating_data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await rate_movie_service(movie_id, rating_data, current_user.id, db)
