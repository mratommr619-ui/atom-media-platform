from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.watch_history import WatchHistory
from backend.schemas.watch_history import WatchHistoryCreate, WatchHistory as WHSchema
from backend.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=WHSchema)
async def add_watch(wh: WatchHistoryCreate, user=Depends(get_current_user), db=Depends(get_db)):
    obj = WatchHistory(user_id=user.id, movie_id=wh.movie_id, series_id=wh.series_id, episode_id=wh.episode_id, video_id=wh.video_id)
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@router.get("/", response_model=list[WHSchema])
async def get_watch_history(user=Depends(get_current_user), db=Depends(get_db)):
    res = await db.execute(WatchHistory.__table__.select().where(WatchHistory.user_id==user.id).order_by(WatchHistory.watched_at.desc()).limit(50))
    return res.scalars().all()