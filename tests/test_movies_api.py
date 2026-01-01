import pytest
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_read_movies_empty(client):
    """Test that a fresh DB returns an empty paginated response."""
    response = await client.get(
        "/api/v1/movies/",
        params={"page": 1, "size": 10, "sort_by": "rating", "order": "desc"},
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_create_movie_unauthorized(client):
    """Test that you cannot create a movie without a token."""
    response = await client.post(
        "/api/v1/movies/", json={"title": "Hacker Movie", "director": "Anonymous"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_movie_authorized(authorized_client, test_user):
    """
    Test creating a movie using the pre-authorized client.
    No manual token creation needed here!
    """
    payload = {"title": "Authorized Movie", "director": "Pytest"}
    response = await authorized_client.post("/api/v1/movies/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Authorized Movie"
    assert data["user_id"] == test_user.id


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

    response = await client.get(
        "/api/v1/movies/",
        headers=headers,
        params={"page": 1, "size": 10, "sort_by": "rating", "order": "desc"},
    )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_delete_movie_owner(authorized_client, test_user, db_session):
    """Test that the owner can delete their movie."""
    res = await authorized_client.post(
        "/api/v1/movies/", json={"title": "To Delete", "director": "Me"}
    )
    movie_id = res.json()["id"]

    del_res = await authorized_client.delete(f"/api/v1/movies/{movie_id}")
    assert del_res.status_code == 204

    del_res_again = await authorized_client.delete(f"/api/v1/movies/{movie_id}")
    assert del_res_again.status_code == 404
