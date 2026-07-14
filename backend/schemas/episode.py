from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.schemas.video import Video

class EpisodeBase(BaseModel):
    series_id: int
    episode_number: int
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_published: bool = False

class EpisodeCreate(EpisodeBase):
    pass

class EpisodeUpdate(BaseModel):
    episode_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_published: Optional[bool] = None

class Episode(EpisodeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    videos: List[Video] = []

    class Config:
        from_attributes = True
