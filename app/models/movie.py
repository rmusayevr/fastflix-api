from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text
from app.db.base import Base


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    director: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
