from pydantic import BaseModel
from typing import Optional

class LanguageBase(BaseModel):
    code: str
    name: str
    flag: Optional[str] = None

class LanguageCreate(LanguageBase):
    pass

class LanguageUpdate(BaseModel):
    name: Optional[str] = None
    flag: Optional[str] = None

class Language(LanguageBase):
    id: int

    class Config:
        from_attributes = True
