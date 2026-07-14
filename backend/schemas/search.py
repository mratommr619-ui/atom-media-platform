from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str
    page: int = 1
    per_page: int = 10

class SearchResultItem(BaseModel):
    id: int
    title: str
    type: str
    thumbnail: Optional[str]
    year: Optional[int]
    match_type: str

class SearchResult(BaseModel):
    items: List[SearchResultItem]
    total: int
    page: int
    pages: int

    class Config:
        arbitrary_types_allowed = True
