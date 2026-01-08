import json
from slugify import slugify
from typing import Literal, List
from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    HTTPException,
    Request,
    BackgroundTasks,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import (
    get_db,
    get_current_active_user,
    PermissionChecker,
)
from app.core.limiter import limiter
from app.core.redis import get_redis_client
from app.models.user import UserModel
from app.models.movie import Movie, Genre, CompareRequest
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieResponse, MovieCreate, MovieUpdate
from app.services.movie_service import (
    get_all_movies_service,
    rate_movie_service,
    # get_recommendations_service,
)
from app.schemas.common import PageResponse
from app.schemas.rating import RatingResponse, RatingCreate
from app.services.ai_service import AIService
from app.services.search_service import index_movie, remove_movie_from_index
from app.services.watchlist_service import toggle_watchlist_service
from app.tasks.notification_tasks import broadcast_notification_task

router = APIRouter()


@router.get("/", response_model=PageResponse[MovieResponse])
@limiter.limit("10/minute")
async def read_movies(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: Literal["id", "title", "rating"] = "rating",
    order: Literal["asc", "desc"] = "desc",
    min_rating: float = Query(None, ge=0, le=10),
    search_query: str = Query(None),
):
    return await get_all_movies_service(
        db, page, size, search_query, sort_by, order, min_rating
    )


@router.get("/trending", response_model=list[MovieResponse])
@limiter.limit("5/minute")
async def get_trending_movies(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Fetches the Top 5 Trending movies from the Redis Cache.
    If cache is empty (e.g. first run), falls back to DB or returns empty.
    Rate Limit: 5 per minute per IP.
    """
    redis = get_redis_client()
    cached_data = await redis.get("trending_movies")

    movie_ids = []

    if cached_data:
        data = json.loads(cached_data)
        movie_ids = data.get("movie_ids", [])
        print(f"⚡ Cache Hit! Serving IDs: {movie_ids}")
    else:
        print("⚠️ Cache Miss! (Worker hasn't run yet)")
        return []

    if movie_ids:
        stmt = (
            select(Movie)
            .options(selectinload(Movie.genres))
            .where(Movie.id.in_(movie_ids))
        )
        result = await db.execute(stmt)
        movies = result.scalars().all()

        movies_map = {m.id: m for m in movies}
        ordered_movies = [movies_map[mid] for mid in movie_ids if mid in movies_map]

        return ordered_movies

    return []


@router.get("/semantic_search", response_model=list[MovieResponse])
async def semantic_search(
    query: str, limit: int = 5, db: AsyncSession = Depends(get_db)
):
    """
    🤖 Search movies by meaning.
    E.g., "Movies about sad robots" -> Finds Wall-E.
    """
    repo = MovieRepository(db)
    return await repo.search_semantic(query, limit)


@router.post("/chat")
async def chat_with_movies(question: str, db: AsyncSession = Depends(get_db)):
    """
    🗣️ Ask a question about movies in the database.
    """
    repo = MovieRepository(db)

    relevant_movies = await repo.search_semantic(question, limit=1)

    if not relevant_movies:
        return {"answer": "I couldn't find any movies relevant to your question."}

    top_movie = relevant_movies[0]

    context_text = f"Title: {top_movie.title}. Description: {top_movie.description}"

    answer = AIService.generate_answer(context_text, question)

    return {"question": question, "source_movie": top_movie.title, "answer": answer}


@router.get("/analytics/genres")
async def get_genre_stats(db: AsyncSession = Depends(get_db)):
    """
    📊 Returns top genres and their movie counts.
    """
    repo = MovieRepository(db)
    stats = await repo.get_genre_statistics()
    # Convert list of tuples to list of dicts for JSON
    return [{"genre": row[0], "count": row[1]} for row in stats]


@router.post("/utils/compare_vectors")
async def compare_vectors(payload: CompareRequest):
    """
    🧮 Debug tool to compare two texts semantically.
    """
    score = AIService.calculate_similarity(payload.text1, payload.text2)
    return {"similarity_score": score}


@router.get("/{movie_id}", response_model=MovieResponse)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker("movie:create"))],
)
async def create_movie(
    movie_in: MovieCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    slug = slugify(movie_in.title)

    new_movie = Movie(
        title=movie_in.title,
        slug=slug,
        description=movie_in.description,
        release_year=movie_in.release_year,
        video_url=movie_in.video_url,
        thumbnail_url=movie_in.thumbnail_url,
    )

    if movie_in.genre_ids:
        stmt = select(Genre).where(Genre.id.in_(movie_in.genre_ids))
        result = await db.execute(stmt)
        genres = result.scalars().all()
        if len(genres) != len(movie_in.genre_ids):
            raise HTTPException(
                status_code=404, detail="One or more Genre IDs not found"
            )
        new_movie.genres = list(genres)

    db.add(new_movie)
    await db.commit()

    stmt = (
        select(Movie)
        .options(selectinload(Movie.genres))
        .where(Movie.id == new_movie.id)
    )
    result = await db.execute(stmt)
    fresh_movie = result.scalars().first()
    background_tasks.add_task(index_movie, fresh_movie)
    broadcast_notification_task.delay(f"🎬 New Release: {fresh_movie.title}")
    return fresh_movie


@router.patch(
    "/{movie_id}",
    response_model=MovieResponse,
    dependencies=[Depends(PermissionChecker("movie:update"))],
)
async def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    stmt = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    update_data = movie_in.model_dump(exclude_unset=True)
    genre_ids = update_data.pop("genre_ids", None)

    for field, value in update_data.items():
        setattr(movie, field, value)

    if genre_ids is not None:
        stmt_genres = select(Genre).where(Genre.id.in_(genre_ids))
        genres_result = await db.execute(stmt_genres)
        new_genres = genres_result.scalars().all()
        movie.genres = list(new_genres)

    await db.commit()
    await db.refresh(movie)
    background_tasks.add_task(index_movie, movie)
    return movie


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker("movie:delete"))],
)
async def delete_movie(
    movie_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    stmt = select(Movie).where(Movie.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    await db.delete(movie)
    await db.commit()
    background_tasks.add_task(remove_movie_from_index, movie_id)
    return None


@router.post("/{movie_id}/rate", response_model=RatingResponse)
async def rate_movie(
    movie_id: int,
    rating_data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    return await rate_movie_service(movie_id, rating_data, current_user.id, db)


@router.post("/{movie_id}/watchlist")
async def toggle_watchlist(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    return await toggle_watchlist_service(current_user.id, movie_id, db)


# @router.get("/{movie_id}/recommendations", response_model=List[MovieResponse])
# async def get_movie_recommendations(
#     movie_id: int,
#     db: AsyncSession = Depends(get_db),
# ):
#     return await get_recommendations_service(movie_id, db)


@router.get("/{movie_id}/recommendations", response_model=List[MovieResponse])
async def recommend_movies(
    movie_id: int, limit: int = 5, db: AsyncSession = Depends(get_db)
):
    """
    🍿 "More Like This"
    Returns movies semantically similar to the given movie_id.
    """
    repo = MovieRepository(db)
    recommendations = await repo.get_similar_movies(movie_id, limit)

    if not recommendations:
        return []

    return recommendations
