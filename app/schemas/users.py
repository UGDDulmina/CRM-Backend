from datetime import datetime
from app.models.users import UserRole

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class UserRegister(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"