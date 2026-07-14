from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.schemas.genre import Genre
from backend.schemas.keyword import Keyword
from backend.schemas.alias import Alias
from backend.schemas.episode import Episode

class SeriesBase(BaseModel):
    title: str
    title_mm: Optional[str] = None
    description_en: Optional[str] = None
    description_mm: Optional[str] = None
    poster: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    language_original: Optional[str] = None
    is_published: bool = False
    is_archived: bool = False

class SeriesCreate(SeriesBase):
    genre_ids: Optional[List[int]] = []
    keyword_ids: Optional[List[int]] = []

class SeriesUpdate(BaseModel):
    title: Optional[str] = None
    title_mm: Optional[str] = None
    description_en: Optional[str] = None
    description_mm: Optional[str] = None
    poster: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    language_original: Optional[str] = None
    is_published: Optional[bool] = None
    is_archived: Optional[bool] = None
    genre_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None

class Series(SeriesBase):
    id: int
    created_at: datetime
    updated_at: datetime
    episodes: List[Episode] = []
    genres: List[Genre] = []
    keywords: List[Keyword] = []
    aliases: List[Alias] = []

    class Config:
        from_attributes = True
