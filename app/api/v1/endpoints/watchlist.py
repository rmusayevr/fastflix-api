from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.models.user import UserModel
from app.schemas.movie import MovieResponse
from app.services.watchlist_service import get_user_watchlist_service

router = APIRouter()


@router.get("/", response_model=List[MovieResponse])
async def read_watchlist(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get the current user's watchlist.
    """
    return await get_user_watchlist_service(current_user.id, page, size, db)
