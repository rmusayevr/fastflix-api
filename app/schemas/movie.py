from pydantic import BaseModel, ConfigDict, Field
from typing import List


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
    slug: str

    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str
    description: str
    release_year: int
    video_url: str
    thumbnail_url: str


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    release_year: int = Field(..., ge=1888, le=2100)
    video_url: str | None = None
    thumbnail_url: str | None = None
    genre_ids: list[int] = []

    model_config = ConfigDict(extra="forbid")


class MovieResponse(MovieBase):
    id: int
    slug: str
    average_rating: float = 0.0
    rating_count: int = 0
    is_published: bool
    genres: List[GenreResponse] = []

    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    release_year: int | None = Field(None, ge=1888, le=2100)
    video_url: str | None = None
    thumbnail_url: str | None = None
    genre_ids: list[int] | None = None

    model_config = ConfigDict(extra="forbid")
