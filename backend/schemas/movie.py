from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.schemas.genre import Genre
from backend.schemas.keyword import Keyword
from backend.schemas.alias import Alias
from backend.schemas.video import Video

class MovieBase(BaseModel):
    title: str
    title_mm: Optional[str] = None
    description_en: Optional[str] = None
    description_mm: Optional[str] = None
    thumbnail: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    language_original: Optional[str] = None
    duration: Optional[int] = None
    is_published: bool = False
    is_archived: bool = False

class MovieCreate(MovieBase):
    genre_ids: Optional[List[int]] = []
    keyword_ids: Optional[List[int]] = []

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    title_mm: Optional[str] = None
    description_en: Optional[str] = None
    description_mm: Optional[str] = None
    thumbnail: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    language_original: Optional[str] = None
    duration: Optional[int] = None
    is_published: Optional[bool] = None
    is_archived: Optional[bool] = None
    genre_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None

class Movie(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    genres: List[Genre] = []
    keywords: List[Keyword] = []
    aliases: List[Alias] = []
    videos: List[Video] = []

    class Config:
        from_attributes = True
