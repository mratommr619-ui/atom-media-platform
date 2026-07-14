from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import get_db
from backend.models.episode import Episode
from backend.schemas.episode import Episode as EpSchema, EpisodeCreate, EpisodeUpdate
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.post("/", response_model=EpSchema)
async def create_episode(ep: EpisodeCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Episode(**ep.dict())
    db.add(obj); await db.commit(); await db.refresh(obj)
    result = await db.execute(select(Episode).options(selectinload(Episode.videos)).where(Episode.id == obj.id))
    return result.scalars().first()

@router.get("/{episode_id}", response_model=EpSchema)
async def get_episode(episode_id:int, db=Depends(get_db)):
    result = await db.execute(select(Episode).options(selectinload(Episode.videos)).where(Episode.id == episode_id))
    e = result.scalars().first()
    if not e: raise HTTPException(404)
    return e

@router.put("/{episode_id}", response_model=EpSchema)
async def update_episode(episode_id:int, update:EpisodeUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Episode).options(selectinload(Episode.videos)).where(Episode.id == episode_id))
    e = result.scalars().first()
    if not e: raise HTTPException(404)
    for k,v in update.dict(exclude_unset=True).items(): setattr(e,k,v)
    await db.commit(); await db.refresh(e)
    result = await db.execute(select(Episode).options(selectinload(Episode.videos)).where(Episode.id == episode_id))
    return result.scalars().first()

@router.delete("/{episode_id}")
async def delete_episode(episode_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    e = await db.get(Episode, episode_id)
    if not e: raise HTTPException(404)
    await db.delete(e); await db.commit()
    return {"ok":True}

@router.post("/reorder")
async def reorder_episodes(data: dict, db=Depends(get_db), admin=Depends(get_current_admin)):
    series_id = data['series_id']
    order = data['order']
    for idx, ep_id in enumerate(order, start=1):
        ep = await db.get(Episode, ep_id)
        if ep and ep.series_id == series_id:
            ep.episode_number = idx
    await db.commit()
    return {"ok": True}
