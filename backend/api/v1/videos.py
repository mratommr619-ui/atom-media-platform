from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.video import Video
from backend.schemas.video import Video as VideoSchema, VideoCreate, VideoUpdate
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.post("/", response_model=VideoSchema)
async def add_video(video: VideoCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Video(**video.dict())
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@router.put("/{video_id}", response_model=VideoSchema)
async def update_video(video_id:int, update:VideoUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    v = await db.get(Video, video_id)
    if not v: raise HTTPException(404)
    for k,val in update.dict(exclude_unset=True).items(): setattr(v,k,val)
    await db.commit(); await db.refresh(v); return v

@router.delete("/{video_id}")
async def delete_video(video_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    v = await db.get(Video, video_id)
    if not v: raise HTTPException(404)
    await db.delete(v); await db.commit()
    return {"ok":True}