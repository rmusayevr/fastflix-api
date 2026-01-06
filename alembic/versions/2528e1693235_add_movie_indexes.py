"""add_movie_indexes

Revision ID: 2528e1693235
Revises: 71a8a49bf5e0
Create Date: 2026-01-06 18:10:35.474760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2528e1693235"
down_revision: Union[str, Sequence[str], None] = "71a8a49bf5e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_movies_release_year",
        "movies",
        ["release_year"],
        unique=False,
        if_not_exists=True,
    )

    op.create_index(
        "ix_movies_rating",
        "movies",
        ["average_rating"],
        unique=False,
        if_not_exists=True,
    )

    op.create_index(
        "ix_movies_slug", "movies", ["slug"], unique=True, if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index("ix_movies_slug", table_name="movies")
    op.drop_index("ix_movies_rating", table_name="movies")
    op.drop_index("ix_movies_release_year", table_name="movies")
