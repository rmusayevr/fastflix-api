from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
)
from app.db.base import Base
from app.models.mixins import TimestampMixin
from typing import TYPE_CHECKING, List
import datetime

if TYPE_CHECKING:
    from app.models.rating import RatingModel
    from app.models.watchlist import WatchlistModel
    from app.models.rbac import RoleModel


class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role: Mapped["RoleModel"] = relationship(
        "RoleModel", back_populates="users", lazy="joined"
    )

    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    ratings: Mapped[List["RatingModel"]] = relationship(
        "RatingModel", back_populates="user"
    )
    watchlist: Mapped["WatchlistModel"] = relationship(
        "WatchlistModel", back_populates="user"
    )
    notifications = relationship(
        "NotificationModel", back_populates="user", cascade="all, delete-orphan"
    )
