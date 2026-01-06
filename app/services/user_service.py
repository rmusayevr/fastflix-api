import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.models.user import UserModel
from app.models.rbac import RoleModel
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password


async def get_default_role(db: AsyncSession):
    """Helper to fetch the default 'user' role"""
    stmt = select(RoleModel).where(RoleModel.name == "user")
    result = await db.execute(stmt)
    return result.scalars().first()


async def register_user_service(user: UserCreate, db: AsyncSession) -> UserModel:
    repo = UserRepository(db)
    if await repo.get_by_email(user.email):
        raise ValueError("Email already registered")

    hashed_pwd = get_password_hash(user.password)

    default_role = await get_default_role(db)

    db_obj = UserModel(
        email=user.email,
        hashed_password=hashed_pwd,
        full_name=user.full_name,
        is_active=True,
        is_superuser=False,
        role_id=default_role.id if default_role else None,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def authenticate_user(db: AsyncSession, email: str, password: str):
    repo = UserRepository(db)
    user = await repo.get_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_or_create_google_user(email: str, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if user:
        return user

    random_password = str(uuid.uuid4())
    hashed_pw = get_password_hash(random_password)

    default_role = await get_default_role(db)

    new_user = UserModel(
        email=email,
        hashed_password=hashed_pw,
        is_active=True,
        is_superuser=False,
        role_id=default_role.id if default_role else None,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
