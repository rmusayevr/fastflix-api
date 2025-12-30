import pytest
from app.schemas.movie import MovieCreate
from app.services.movie_service import create_movie_service, delete_movie_service
from app.models.movie import MovieModel
from app.models.user import UserModel
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException


@pytest.mark.asyncio
async def test_create_movie(db_session, test_user):
    movie_data = MovieCreate(title="Inception", director="Christopher Nolan")

    new_movie = await create_movie_service(movie_data, test_user.id, db_session)

    assert new_movie.title == "Inception"
    assert new_movie.user_id == test_user.id
    assert new_movie.id is not None


@pytest.mark.asyncio
async def test_delete_movie_success(db_session, test_user):
    movie = MovieModel(title="To Delete", director="Me", user_id=test_user.id)
    db_session.add(movie)
    await db_session.commit()

    await delete_movie_service(movie.id, test_user.id, db_session)

    with pytest.raises(MovieNotFoundException):
        await delete_movie_service(movie.id, test_user.id, db_session)


@pytest.mark.asyncio
async def test_delete_movie_unauthorized(db_session, test_user):
    other_user = UserModel(
        email="other_user@example.com",
        hashed_password="fakehashedpassword",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    movie = MovieModel(
        title="Not Mine",
        director="Someone Else",
        user_id=other_user.id,
    )
    db_session.add(movie)
    await db_session.commit()

    with pytest.raises(NotAuthorizedException):
        await delete_movie_service(movie.id, test_user.id, db_session)
