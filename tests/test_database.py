import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """
    This test proves that:
    1. The fixture works (we got a session).
    2. The database is reachable (Postgres is running).
    """
    result = await db_session.execute(text("SELECT 1"))

    scalar_result = result.scalar()
    assert scalar_result == 1
