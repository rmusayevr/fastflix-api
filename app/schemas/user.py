from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=100)

    model_config = ConfigDict(extra="forbid")


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    avatar: str | None = None

    class Config:
        from_attributes = True


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8)
