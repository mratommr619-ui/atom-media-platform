from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.user import User
from backend.models.movie import Movie
from backend.models.series import Series
from backend.models.episode import Episode
from backend.models.video import Video
from backend.models.report import Report
from datetime import datetime
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.get("/")
async def dashboard(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    total_users = await db.scalar(select(func.count(User.id)))
    today = datetime.utcnow().date()
    today_users = await db.scalar(select(func.count(User.id)).where(func.date(User.join_date) == today))
    total_movies = await db.scalar(select(func.count(Movie.id)))
    total_series = await db.scalar(select(func.count(Series.id)))
    total_episodes = await db.scalar(select(func.count(Episode.id)))
    total_videos = await db.scalar(select(func.count(Video.id)))
    open_reports = await db.scalar(select(func.count(Report.id)).where(Report.status == 'open'))
    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_movies": total_movies,
        "total_series": total_series,
        "total_episodes": total_episodes,
        "total_videos": total_videos,
        "open_reports": open_reports
    }
