from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from app.db.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.rating import RatingModel
    from app.models.watchlist import WatchlistModel


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    director: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner = relationship("UserModel", back_populates="movies")
    ratings: Mapped[List["RatingModel"]] = relationship(
        "RatingModel", back_populates="movie"
    )
    watchlist_users: Mapped["WatchlistModel"] = relationship(
        "WatchlistModel", back_populates="movie"
    )
