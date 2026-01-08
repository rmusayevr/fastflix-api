import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel
from app.db.base import Base
from app.models.mixins import TimestampMixin


class TSVector(TypeDecorator):
    impl = TSVECTOR
    cache_ok = True


movie_genres_link = sa.Table(
    "movie_genres",
    Base.metadata,
    sa.Column("movie_id", sa.ForeignKey("movies.id"), primary_key=True),
    sa.Column("genre_id", sa.ForeignKey("genres.id"), primary_key=True),
)


class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String, unique=True, index=True)
    slug: Mapped[str] = mapped_column(sa.String, unique=True, index=True)
    movies = relationship("Movie", secondary=movie_genres_link, back_populates="genres")


class Movie(Base, TimestampMixin):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(sa.String, index=True)
    slug: Mapped[str] = mapped_column(sa.String, unique=True, index=True)
    description: Mapped[str] = mapped_column(sa.Text)

    video_url: Mapped[str] = mapped_column(sa.String)
    thumbnail_url: Mapped[str] = mapped_column(sa.String)
    release_year: Mapped[int] = mapped_column(sa.Integer)
    is_published: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    average_rating: Mapped[float] = mapped_column(sa.Float, default=0.0, index=True)
    rating_count: Mapped[int] = mapped_column(sa.Integer, default=0)

    search_vector: Mapped[str] = mapped_column(
        TSVector(),
        sa.Computed(
            "to_tsvector('english', title || ' ' || description)", persisted=True
        ),
    )

    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)

    genres = relationship("Genre", secondary=movie_genres_link, back_populates="movies")
    ratings = relationship(
        "RatingModel", back_populates="movie", cascade="all, delete-orphan"
    )
    watchlist = relationship(
        "WatchlistModel", back_populates="movie", cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.Index("ix_movies_search_vector", "search_vector", postgresql_using="gin"),
    )


class CompareRequest(BaseModel):
    text1: str
    text2: str
