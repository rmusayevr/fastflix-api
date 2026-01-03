from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, CheckConstraint, UniqueConstraint
from app.db.base import Base


class RatingModel(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    score: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))

    user = relationship("UserModel", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 10", name="check_score_range"),
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_rating"),
    )
