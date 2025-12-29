from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.movie import Movie, MovieCreate

router = APIRouter()

MOVIE_DATABASE = [
    {"id": 1, "title": "Dead Poets Society", "director": "Peter Weir"},
    {"id": 2, "title": "Midnight in Paris", "director": "Woody Allen"},
    {"id": 3, "title": "The Prestige", "director": "Christopher Nolan"},
]


@router.get("/", response_model=List[Movie])
async def read_movies():
    return MOVIE_DATABASE


@router.post("/", response_model=Movie, status_code=201)
async def create_movie(movie: MovieCreate):
    new_id = len(MOVIE_DATABASE) + 1
    movie_data = movie.model_dump()
    movie_data["id"] = new_id

    MOVIE_DATABASE.append(movie_data)
    return movie_data
