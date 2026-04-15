import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    email_verified: bool
    full_name: str | None
    picture_url: str | None
    locale: str | None
    auth_provider: str
    is_active: bool
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthSessionResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    last_seen_at: datetime | None
    user_agent: str | None
    ip_address: str | None
    current: bool

    model_config = {"from_attributes": True}
