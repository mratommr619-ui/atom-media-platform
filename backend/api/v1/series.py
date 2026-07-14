from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import get_db
from backend.models.series import Series
from backend.models.episode import Episode
from backend.models.genre import Genre
from backend.models.keyword import Keyword
from backend.schemas.series import Series as SeriesSchema, SeriesCreate, SeriesUpdate
from backend.schemas.common import PaginatedResponse
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[SeriesSchema])
async def list_series(page:int=1, per_page:int=20, search:str=None, db=Depends(get_db)):
    filters = [Series.is_published == True]
    if search:
        filters.append(Series.title.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count(Series.id)).where(*filters))
    query = (
        select(Series)
        .options(selectinload(Series.episodes).selectinload(Episode.videos), selectinload(Series.genres), selectinload(Series.keywords), selectinload(Series.aliases))
        .where(*filters)
        .order_by(Series.created_at.desc())
    )
    query = query.offset((page-1)*per_page).limit(per_page)
    results = await db.execute(query)
    series = results.scalars().all()
    return {"items": series, "total": total, "page": page, "per_page": per_page, "pages": (total+per_page-1)//per_page}

@router.post("/", response_model=SeriesSchema)
async def create_series(series: SeriesCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Series(**series.dict(exclude={'genre_ids','keyword_ids'}))
    if series.genre_ids: obj.genres = (await db.execute(select(Genre).where(Genre.id.in_(series.genre_ids)))).scalars().all()
    if series.keyword_ids: obj.keywords = (await db.execute(select(Keyword).where(Keyword.id.in_(series.keyword_ids)))).scalars().all()
    db.add(obj); await db.commit(); await db.refresh(obj)
    result = await db.execute(
        select(Series)
        .options(selectinload(Series.episodes).selectinload(Episode.videos), selectinload(Series.genres), selectinload(Series.keywords), selectinload(Series.aliases))
        .where(Series.id == obj.id)
    )
    return result.scalars().first()

@router.get("/{series_id}", response_model=SeriesSchema)
async def get_series(series_id:int, db=Depends(get_db)):
    result = await db.execute(
        select(Series)
        .options(selectinload(Series.episodes).selectinload(Episode.videos), selectinload(Series.genres), selectinload(Series.keywords), selectinload(Series.aliases))
        .where(Series.id == series_id)
    )
    s = result.scalars().first()
    if not s: raise HTTPException(404)
    return s

@router.put("/{series_id}", response_model=SeriesSchema)
async def update_series(series_id:int, update:SeriesUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(
        select(Series)
        .options(selectinload(Series.episodes).selectinload(Episode.videos), selectinload(Series.genres), selectinload(Series.keywords), selectinload(Series.aliases))
        .where(Series.id == series_id)
    )
    s = result.scalars().first()
    if not s: raise HTTPException(404)
    for k,v in update.dict(exclude_unset=True).items():
        if k not in ('genre_ids','keyword_ids'): setattr(s,k,v)
    if update.genre_ids is not None: s.genres = (await db.execute(select(Genre).where(Genre.id.in_(update.genre_ids)))).scalars().all()
    if update.keyword_ids is not None: s.keywords = (await db.execute(select(Keyword).where(Keyword.id.in_(update.keyword_ids)))).scalars().all()
    await db.commit(); await db.refresh(s)
    result = await db.execute(
        select(Series)
        .options(selectinload(Series.episodes).selectinload(Episode.videos), selectinload(Series.genres), selectinload(Series.keywords), selectinload(Series.aliases))
        .where(Series.id == series_id)
    )
    return result.scalars().first()

@router.delete("/{series_id}")
async def delete_series(series_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    s = await db.get(Series, series_id)
    if not s: raise HTTPException(404)
    await db.delete(s); await db.commit()
    return {"ok":True}
