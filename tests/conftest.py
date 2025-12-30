import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.core.config import settings
from app.main import app
from app.models.user import UserModel


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session")
def async_sessionmaker(engine):
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(
    async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
            await session.commit()

        await session.close()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password="fakehashedpassword",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Create a new AsyncClient for every test.
    We override the 'get_db' dependency to use our test 'db_session'.
    """
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
