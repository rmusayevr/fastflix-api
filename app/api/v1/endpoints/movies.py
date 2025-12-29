from fastapi import APIRouter

router = APIRouter()

MOVIE_DATABASE = [
    {"id": 1, "title": "Dead Poets Society", "director": "Peter Weir"},
    {"id": 2, "title": "Midnight in Paris", "director": "Woody Allen"},
    {"id": 3, "title": "The Prestige", "director": "Christopher Nolan"},
]


@router.get("/")
async def read_movies():
    """
    Retrieve a list of all movies.
    """
    return MOVIE_DATABASE
