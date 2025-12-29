from typing import List, Dict, Any
from app.schemas.movie import MovieCreate


def create_movie_service(
    movie: MovieCreate, db: List[Dict[str, Any]]
) -> Dict[str, Any]:
    new_id = len(db) + 1

    movie_data = movie.model_dump()
    movie_data["id"] = new_id

    db.append(movie_data)

    return movie_data


def get_all_movies_service(db: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return db
