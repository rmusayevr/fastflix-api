from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.schemas.movie import Movie, MovieCreate
from app.api.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[Movie])
async def read_movies(db: List[Dict[str, Any]] = Depends(get_db)):
    return db


@router.post("/", response_model=Movie, status_code=201)
async def create_movie(movie: MovieCreate, db: List[Dict[str, Any]] = Depends(get_db)):
    new_id = len(db) + 1

    movie_data = movie.model_dump()
    movie_data["id"] = new_id

    db.append(movie_data)
    return movie_data
