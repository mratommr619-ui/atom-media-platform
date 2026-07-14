from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    language: Optional[str] = None
    role: UserRole = UserRole.user
    status: UserStatus = UserStatus.active

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_premium: Optional[bool] = None
    ads_disabled: Optional[bool] = None

class User(UserBase):
    id: int
    join_date: datetime
    last_active: datetime
    is_premium: bool = False
    ads_disabled: bool = False
    warnings: int = 0

    class Config:
        from_attributes = True

