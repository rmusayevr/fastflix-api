from pydantic import BaseModel
from typing import List


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int

    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str
    description: str
    release_year: int
    video_url: str
    thumbnail_url: str


class MovieCreate(MovieBase):
    genre_ids: List[int] = []


class MovieResponse(MovieBase):
    id: int
    is_published: bool
    genres: List[GenreResponse] = []

    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    release_year: int | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    is_published: bool | None = None
    genre_ids: List[int] | None = None
