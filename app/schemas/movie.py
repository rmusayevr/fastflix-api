from pydantic import BaseModel, Field
from typing import Optional


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, example="Inception")
    director: str = Field(..., min_length=1, example="Christopher Nolan")
    description: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    id: int

    class Config:
        from_attributes = True
