import pytest
from app.schemas.movie import MovieCreate, MovieUpdate
from app.services.movie_service import (
    get_movie_by_id_service,
    create_movie_service,
    update_movie_service,
    delete_movie_service,
)
from app.models.movie import MovieModel
from app.models.user import UserModel
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException


@pytest.mark.asyncio
async def test_get_movie_by_id_success(db_session, test_user):
    movie = MovieModel(
        title="Interstellar",
        director="Christopher Nolan",
        user_id=test_user.id,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    found_movie = await get_movie_by_id_service(movie.id, db_session)

    assert found_movie.id == movie.id
    assert found_movie.title == "Interstellar"


@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(db_session):
    with pytest.raises(MovieNotFoundException):
        await get_movie_by_id_service(999999, db_session)


@pytest.mark.asyncio
async def test_create_movie(db_session, test_user):
    movie_data = MovieCreate(title="Inception", director="Christopher Nolan")

    new_movie = await create_movie_service(movie_data, test_user.id, db_session)

    assert new_movie.title == "Inception"
    assert new_movie.user_id == test_user.id
    assert new_movie.id is not None


@pytest.mark.asyncio
async def test_update_movie_success(db_session, test_user):
    movie = MovieModel(
        title="Old Title",
        director="Old Director",
        user_id=test_user.id,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    update_data = MovieUpdate(
        title="New Title",
        director="New Director",
    )

    updated_movie = await update_movie_service(
        movie_id=movie.id,
        update_data=update_data,
        user_id=test_user.id,
        db=db_session,
    )

    assert updated_movie.title == "New Title"
    assert updated_movie.director == "New Director"


@pytest.mark.asyncio
async def test_update_movie_not_found(db_session, test_user):
    update_data = MovieUpdate(title="Doesn't Matter")

    with pytest.raises(MovieNotFoundException):
        await update_movie_service(
            movie_id=999999,
            update_data=update_data,
            user_id=test_user.id,
            db=db_session,
        )


@pytest.mark.asyncio
async def test_update_movie_unauthorized(db_session, test_user):
    other_user = UserModel(
        email="unauthorized_user@example.com",
        hashed_password="fakehashedpassword",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    movie = MovieModel(
        title="Private Movie",
        director="Secret",
        user_id=other_user.id,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    update_data = MovieUpdate(title="Hacked Title")

    with pytest.raises(NotAuthorizedException):
        await update_movie_service(
            movie_id=movie.id,
            update_data=update_data,
            user_id=test_user.id,
            db=db_session,
        )


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
