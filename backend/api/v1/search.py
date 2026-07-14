from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.search import SearchResult, SearchRequest
from backend.services.search import search_content

router = APIRouter()

@router.get("/", response_model=SearchResult)
async def search(q: str = Query(...), page: int = 1, per_page: int = 10, request: Request = None, db: AsyncSession = Depends(get_db)):
    embedding_service = request.app.state.embedding_service
    items, total = await search_content(db, q, embedding_service, page, per_page)
    return SearchResult(items=items, total=total, page=page, pages=max(1, (total+per_page-1)//per_page))