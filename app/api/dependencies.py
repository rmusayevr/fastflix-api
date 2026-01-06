from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import UserModel
from app.models.rbac import RoleModel
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)


async def get_db():
    """
    Dependency that creates a new database session for each request
    and closes it afterwards.
    """
    async with AsyncSessionLocal() as db:
        yield db


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Validates the JWT token and fetches the user from the database.
    Also eagerly loads the 'role' and 'permissions' for RBAC checks.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    stmt = (
        select(UserModel)
        .options(selectinload(UserModel.role).selectinload(RoleModel.permissions))
        .where(UserModel.id == token_data.sub)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Ensures the user account is marked as 'active'.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """
    Legacy Admin check.
    Use PermissionChecker for granular permissions instead!
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


class PermissionChecker:
    """
    RBAC Dependency.
    Checks if the current user has the specific required permission.

    Usage: dependencies=[Depends(PermissionChecker("movie:create"))]
    """

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self, current_user: UserModel = Depends(get_current_active_user)
    ):
        if current_user.is_superuser:
            return True

        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned.",
            )

        user_permissions = {p.name for p in current_user.role.permissions}

        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission: {self.required_permission}",
            )

        return True
