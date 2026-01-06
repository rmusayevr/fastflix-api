import uuid
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


async def authenticate_user(db: AsyncSession, email: str, password: str):
    repo = UserRepository(db)

    user = await repo.get_by_email(email)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_or_create_google_user(email: str, db: AsyncSession):
    """
    If user exists, return them.
    If not, create them with a random password and return them.
    """
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if user:
        return user

    random_password = str(uuid.uuid4())
    hashed_pw = get_password_hash(random_password)

    new_user_data = UserCreate(
        email=email,
        password=random_password,
        full_name="Google User",
    )

    new_user = UserModel(
        email=email, hashed_password=hashed_pw, is_active=True, is_superuser=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
