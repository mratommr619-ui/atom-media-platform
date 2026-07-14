from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WatchHistoryBase(BaseModel):
    user_id: int
    movie_id: Optional[int] = None
    series_id: Optional[int] = None
    episode_id: Optional[int] = None
    video_id: Optional[int] = None

class WatchHistoryCreate(WatchHistoryBase):
    pass

class WatchHistory(WatchHistoryBase):
    id: int
    watched_at: datetime

    class Config:
        from_attributes = True
