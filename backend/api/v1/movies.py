from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import get_db
from backend.models.movie import Movie
from backend.models.genre import Genre
from backend.models.keyword import Keyword
from backend.schemas.movie import Movie as MovieSchema, MovieCreate, MovieUpdate
from backend.schemas.common import PaginatedResponse
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[MovieSchema])
async def list_movies(page: int=1, per_page:int=20, search:str=None, db=Depends(get_db)):
    filters = [Movie.is_published == True]
    if search:
        filters.append(Movie.title.ilike(f"%{search}%"))
    total = await db.scalar(select(func.count(Movie.id)).where(*filters))
    query = (
        select(Movie)
        .options(selectinload(Movie.genres), selectinload(Movie.keywords), selectinload(Movie.aliases), selectinload(Movie.videos))
        .where(*filters)
        .order_by(Movie.created_at.desc())
    )
    query = query.offset((page-1)*per_page).limit(per_page)
    results = await db.execute(query)
    movies = results.scalars().all()
    return {"items": movies, "total": total, "page": page, "per_page": per_page, "pages": (total+per_page-1)//per_page}

@router.post("/", response_model=MovieSchema)
async def create_movie(movie: MovieCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Movie(**movie.dict(exclude={'genre_ids','keyword_ids'}))
    if movie.genre_ids: obj.genres = (await db.execute(select(Genre).where(Genre.id.in_(movie.genre_ids)))).scalars().all()
    if movie.keyword_ids: obj.keywords = (await db.execute(select(Keyword).where(Keyword.id.in_(movie.keyword_ids)))).scalars().all()
    db.add(obj); await db.commit(); await db.refresh(obj)
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres), selectinload(Movie.keywords), selectinload(Movie.aliases), selectinload(Movie.videos))
        .where(Movie.id == obj.id)
    )
    return result.scalars().first()

@router.get("/{movie_id}", response_model=MovieSchema)
async def get_movie(movie_id:int, db=Depends(get_db)):
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres), selectinload(Movie.keywords), selectinload(Movie.aliases), selectinload(Movie.videos))
        .where(Movie.id == movie_id)
    )
    m = result.scalars().first()
    if not m: raise HTTPException(404)
    return m

@router.put("/{movie_id}", response_model=MovieSchema)
async def update_movie(movie_id:int, update:MovieUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres), selectinload(Movie.keywords), selectinload(Movie.aliases), selectinload(Movie.videos))
        .where(Movie.id == movie_id)
    )
    m = result.scalars().first()
    if not m: raise HTTPException(404)
    for k,v in update.dict(exclude_unset=True).items():
        if k not in ('genre_ids','keyword_ids'): setattr(m,k,v)
    if update.genre_ids is not None: m.genres = (await db.execute(select(Genre).where(Genre.id.in_(update.genre_ids)))).scalars().all()
    if update.keyword_ids is not None: m.keywords = (await db.execute(select(Keyword).where(Keyword.id.in_(update.keyword_ids)))).scalars().all()
    await db.commit(); await db.refresh(m)
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres), selectinload(Movie.keywords), selectinload(Movie.aliases), selectinload(Movie.videos))
        .where(Movie.id == movie_id)
    )
    return result.scalars().first()

@router.delete("/{movie_id}")
async def delete_movie(movie_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    m = await db.get(Movie, movie_id)
    if not m: raise HTTPException(404)
    await db.delete(m); await db.commit()
    return {"ok":True}
