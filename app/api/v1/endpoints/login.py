from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.api.dependencies import get_db
from app.core import security
from app.core.oauth import oauth
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.services.user_service import authenticate_user, get_or_create_google_user
from app.schemas.token import Token

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str,
) -> Any:
    """
    Use a valid Refresh Token to get a new Access Token.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_type = payload.get("type")
        user_id = payload.get("sub")

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    new_access_token = security.create_access_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/google")
async def google_login(request: Request):
    """
    Redirects the user to the Google Login page.
    """
    redirect_uri = request.url_for("google_auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_auth")
async def google_auth(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Auth Failed: {str(e)}")

    user_info = token.get("userinfo")

    if not user_info:
        user_info = await oauth.google.userinfo(token=token)

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    user = await get_or_create_google_user(email, db)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.email,
    }
