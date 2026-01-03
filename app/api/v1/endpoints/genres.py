from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify

from app.models.movie import Genre
from app.schemas.movie import GenreCreate, GenreResponse
from app.api.dependencies import get_db, get_current_admin

router = APIRouter()


@router.post("/", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre_in: GenreCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    result = await db.execute(select(Genre).where(Genre.name == genre_in.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Genre already exists")

    slug = slugify(genre_in.name)

    new_genre = Genre(name=genre_in.name, slug=slug)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre


@router.get("/", response_model=list[GenreResponse])
async def list_genres(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Genre).offset(skip).limit(limit))
    return result.scalars().all()
