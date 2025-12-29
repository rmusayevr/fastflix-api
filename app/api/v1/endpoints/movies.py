from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.schemas.movie import MovieResponse, MovieCreate
from app.api.dependencies import get_db

from app.services.movie_service import create_movie_service, get_all_movies_service

router = APIRouter()


@router.get("/", response_model=List[MovieResponse])
async def read_movies(db: List[Dict[str, Any]] = Depends(get_db)):
    return get_all_movies_service(db)


@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(movie: MovieCreate, db: List[Dict[str, Any]] = Depends(get_db)):
    return create_movie_service(movie, db)
