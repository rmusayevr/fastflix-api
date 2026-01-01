from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rating import RatingModel


class RatingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_rating(self, user_id: int, movie_id: int) -> RatingModel | None:
        query = select(RatingModel).where(
            RatingModel.user_id == user_id, RatingModel.movie_id == movie_id
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_rating(
        self, user_id: int, movie_id: int, score: int
    ) -> RatingModel:
        rating = RatingModel(user_id=user_id, movie_id=movie_id, score=score)
        self.session.add(rating)
        await self.session.commit()
        await self.session.refresh(rating)
        return rating

    async def update_rating(self, rating: RatingModel, new_score: int) -> RatingModel:
        rating.score = new_score
        await self.session.commit()
        await self.session.refresh(rating)
        return rating
