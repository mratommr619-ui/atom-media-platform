from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.favorite import Favorite
from backend.schemas.favorite import FavoriteCreate, Favorite as FavSchema
from backend.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=FavSchema)
async def add_favorite(fav: FavoriteCreate, user=Depends(get_current_user), db=Depends(get_db)):
    obj = Favorite(user_id=user.id, movie_id=fav.movie_id, series_id=fav.series_id)
    db.add(obj); await db.commit(); await db.refresh(obj); return obj

@router.get("/", response_model=list[FavSchema])
async def list_favorites(user=Depends(get_current_user), db=Depends(get_db)):
    res = await db.execute(Favorite.__table__.select().where(Favorite.user_id==user.id))
    return res.scalars().all()

@router.delete("/{favorite_id}")
async def remove_favorite(favorite_id:int, user=Depends(get_current_user), db=Depends(get_db)):
    fav = await db.get(Favorite, favorite_id)
    if not fav or fav.user_id != user.id: raise HTTPException(404)
    await db.delete(fav); await db.commit()
    return {"ok":True}