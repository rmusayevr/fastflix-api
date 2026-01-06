from pydantic import BaseModel


class MovieSearchDoc(BaseModel):
    id: int
    title: str
    description: str | None = None
    release_year: int
    rating: float
    thumbnail_url: str | None = None
    slug: str
    genres: list[str] = []
