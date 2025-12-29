from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.models.user import UserModel
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password


async def register_user_service(user: UserCreate, db: AsyncSession) -> UserModel:
    repo = UserRepository(db)
    if await repo.get_by_email(user.email):
        raise ValueError("Email already registered")

    hashed_pwd = get_password_hash(user.password)

    return await repo.create(user, hashed_pwd)


async def authenticate_user_service(
    email: str, password: str, db: AsyncSession
) -> UserModel | None:
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
