from typing import Generator, List, Dict, Any
from app.db.session import MOVIE_DATABASE


def get_db() -> Generator[List[Dict[str, Any]], None, None]:
    try:
        db = MOVIE_DATABASE
        yield db
    finally:
        pass
