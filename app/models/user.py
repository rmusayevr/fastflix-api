from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean
from app.db.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.rating import RatingModel
    from app.models.watchlist import WatchlistModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    movies = relationship("MovieModel", back_populates="owner")
    ratings: Mapped[List["RatingModel"]] = relationship(
        "RatingModel", back_populates="user"
    )
    watchlist: Mapped["WatchlistModel"] = relationship(
        "WatchlistModel", back_populates="user"
    )
