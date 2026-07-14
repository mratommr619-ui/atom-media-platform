from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdvertisementBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    media_url: Optional[str] = None
    link: Optional[str] = None
    duration: int = Field(default=15, ge=1, le=120)
    is_active: bool = True


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    media_url: Optional[str] = None
    link: Optional[str] = None
    duration: Optional[int] = Field(default=None, ge=1, le=120)
    is_active: Optional[bool] = None


class Advertisement(AdvertisementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
