import pytest
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_read_movies_empty(client):
    """Test that a fresh DB returns an empty list."""
    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_movie_unauthorized(client):
    """Test that you cannot create a movie without a token."""
    response = await client.post(
        "/api/v1/movies/", json={"title": "Hacker Movie", "director": "Anonymous"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_movie_authorized(client, test_user):
    """Test creating a movie with a valid user token."""
    token = create_access_token(subject=test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"title": "Integration Test Movie", "director": "Pytest"}
    response = await client.post("/api/v1/movies/", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Integration Test Movie"
    assert data["user_id"] == test_user.id
    assert "id" in data


@pytest.mark.asyncio
async def test_read_movies_list(client, test_user):
    """Test that the GET list endpoint returns data."""

    token = create_access_token(subject=test_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/movies/", json={"title": "M1", "director": "D1"}, headers=headers
    )
    await client.post(
        "/api/v1/movies/", json={"title": "M2", "director": "D2"}, headers=headers
    )

    response = await client.get("/api/v1/movies/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
