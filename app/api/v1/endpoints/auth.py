import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import register_user_service, authenticate_user_service
from app.core.security import create_access_token
from app.models.user import UserModel
from app.tasks.email_tasks import send_welcome_email
from app.utils.storage import upload_file_to_s3

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user_service(user_in, db)
        send_welcome_email.delay(user.email)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user_service(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Fetch the current logged-in user.
    This route is protected.
    """
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a profile picture to S3/MinIO and update the user profile.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG images allowed")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"users/{current_user.id}/avatar_{uuid.uuid4()}.{file_extension}"

    avatar_url = await upload_file_to_s3(file, unique_filename)

    current_user.avatar = avatar_url
    await db.commit()
    await db.refresh(current_user)

    return current_user
