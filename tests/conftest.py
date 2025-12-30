import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings
from app.main import app

engine = create_async_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a fresh database session for a test.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()
