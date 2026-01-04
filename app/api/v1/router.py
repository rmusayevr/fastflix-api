from fastapi import APIRouter
from app.api.v1.endpoints import auth, movies, watchlist, genres, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(genres.router, prefix="/genres", tags=["Genres"])
api_router.include_router(movies.router, prefix="/movies", tags=["Movies"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)
