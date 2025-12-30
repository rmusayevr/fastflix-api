from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.api.dependencies import get_db, get_current_user
from app.models.user import UserModel
from app.services.movie_service import (
    create_movie_service,
    get_all_movies_service,
    get_movie_by_id_service,
    update_movie_service,
    delete_movie_service,
)

router = APIRouter()


@router.get("/", response_model=List[MovieResponse])
async def read_movies(db: AsyncSession = Depends(get_db)):
    return await get_all_movies_service(db)


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
    movie_id: int, movie_in: MovieUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_movie_service(movie_id, movie_in, db)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    await delete_movie_service(movie_id, db)
