from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base


class WatchlistModel(Base):
    __tablename__ = "watchlist"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("UserModel", back_populates="watchlist")
    movie = relationship("Movie", back_populates="watchlist")
