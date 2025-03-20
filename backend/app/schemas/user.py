from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    """Base schema for user data."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""
    username: Optional[str] = None
    user_id: Optional[int] = None