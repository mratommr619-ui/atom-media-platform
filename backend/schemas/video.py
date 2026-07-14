from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VideoBase(BaseModel):
    movie_id: Optional[int] = None
    episode_id: Optional[int] = None
    quality: str
    chat_id: int
    message_id: int
    file_id: str
    duration: Optional[int] = None
    resolution: Optional[str] = None
    file_size: Optional[int] = None
    verified: bool = False

class VideoCreate(VideoBase):
    pass

class VideoImport(BaseModel):
    telegram_link: str
    quality: str
    movie_id: Optional[int] = None
    episode_id: Optional[int] = None

class VideoUpdate(BaseModel):
    quality: Optional[str] = None
    verified: Optional[bool] = None
    file_id: Optional[str] = None

class Video(VideoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
