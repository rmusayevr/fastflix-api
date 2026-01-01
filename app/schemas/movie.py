from pydantic import BaseModel, Field
from typing import Optional


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, example="Inception")
    director: str = Field(..., min_length=1, example="Christopher Nolan")
    description: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    director: str | None = Field(default=None, min_length=1)
    description: str | None = None


class MovieResponse(MovieBase):
    id: int
    user_id: int
    rating: float = 0.0

    class Config:
        from_attributes = True
