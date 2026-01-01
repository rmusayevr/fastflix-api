import uuid
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from fastapi import Request, Response
from fastapi_limiter.depends import RateLimiter

from app.api.dependencies import get_db
from app.db.base import Base
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.user import UserModel


@pytest_asyncio.fixture(autouse=True)
def mock_rate_limiter(monkeypatch):
    """
    Mock the RateLimiter to do nothing.

    IMPORTANT: We cannot use AsyncMock() directly because FastAPI inspects
    the signature of the dependency. AsyncMock has (*args, **kwargs), which
    FastAPI interprets as required query parameters, causing a 422 error.

    We define a function with explicit type hints so FastAPI injects
    Request and Response correctly.
    """

    async def mock_call(self, request: Request, response: Response):
        return True

    monkeypatch.setattr(RateLimiter, "__call__", mock_call)


@pytest_asyncio.fixture(autouse=True)
def mock_redis_client(monkeypatch):
    from app.services import movie_service

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True

    monkeypatch.setattr(movie_service, "redis_client", mock_redis)


@pytest_asyncio.fixture
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


@pytest.fixture
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


@pytest_asyncio.fixture(scope="function")
async def normal_user_token_headers(client, test_user):
    return {"Authorization": f"Bearer {create_access_token(subject=str(test_user.id))}"}


@pytest_asyncio.fixture(scope="function")
async def authorized_client(client, normal_user_token_headers):
    client.headers = {
        **client.headers,
        **normal_user_token_headers,
    }
    return client
