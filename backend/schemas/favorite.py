from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FavoriteBase(BaseModel):
    user_id: int
    movie_id: Optional[int] = None
    series_id: Optional[int] = None

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
