from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services.video_delivery import deliver_protected_video
from backend.models.advertisement import Advertisement
from sqlalchemy import select
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/advertisement")
async def active_advertisement(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Return the current ad only for a valid watch flow."""
    status = await request.app.state.redis.get(f"watch:{token}")
    if status not in {"pending", "verified"}:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    ad = (await db.execute(
        select(Advertisement)
        .where(Advertisement.is_active == True)
        .order_by(Advertisement.updated_at.desc(), Advertisement.id.desc())
        .limit(1)
    )).scalars().first()
    if not ad:
        return {"title": "Advertisement", "media_url": None, "link": None, "duration": 15}
    return {"title": ad.title, "media_url": ad.media_url, "link": ad.link, "duration": ad.duration}

@router.get("/verify")
async def verify_ad(token: str, request: Request):
    redis = request.app.state.redis
    status = await redis.get(f"watch:{token}")
    if not status or status != "pending":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    await redis.setex(f"watch:{token}", 300, "verified")
    return {"status": "verified"}

@router.post("/send_video")
async def send_video(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    redis = request.app.state.redis
    status = await redis.get(f"watch:{token}")
    if status != "verified":
        raise HTTPException(status_code=400, detail="Advertisement not completed. Video cannot be unlocked.")
    try:
        user_id_str, video_id_str = token.split("_", 1)
        user_telegram_id = int(user_id_str)
        video_id = int(video_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")
    try:
        await deliver_protected_video(db=db, telegram_id=user_telegram_id, video_id=video_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        raise HTTPException(status_code=500, detail="Failed to send video")
    await redis.delete(f"watch:{token}")
    return {"message": "Video sent successfully"}
