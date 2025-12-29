from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.movie import MovieResponse, MovieCreate
from app.api.dependencies import get_db
from app.services.movie_service import create_movie_service, get_all_movies_service

router = APIRouter()


@router.get("/", response_model=List[MovieResponse])
async def read_movies(db: AsyncSession = Depends(get_db)):
    return await get_all_movies_service(db)


@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(movie: MovieCreate, db: AsyncSession = Depends(get_db)):
    return await create_movie_service(movie, db)
