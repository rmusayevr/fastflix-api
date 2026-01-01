from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Score between 1 and 10")


class RatingResponse(BaseModel):
    id: int
    score: int
    user_id: int
    movie_id: int

    class Config:
        from_attributes = True
