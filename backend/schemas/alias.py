from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AliasBase(BaseModel):
    name: str
    movie_id: Optional[int] = None
    series_id: Optional[int] = None
    is_approved: bool = False

class AliasCreate(AliasBase):
    pass

class AliasUpdate(BaseModel):
    name: Optional[str] = None
    is_approved: Optional[bool] = None

class Alias(AliasBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
