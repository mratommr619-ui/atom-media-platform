from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.video import VideoImport
from backend.models.video import Video
from backend.services.telegram_import import parse_telegram_link
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.post("/telegram")
async def import_from_telegram(data: VideoImport, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    link_info = await parse_telegram_link(data.telegram_link)
    if not link_info:
        raise HTTPException(status_code=400, detail="Invalid Telegram link")
    chat_id = link_info['chat_id']
    message_id = link_info['message_id']
    video = Video(
        movie_id=data.movie_id,
        episode_id=data.episode_id,
        quality=data.quality,
        chat_id=chat_id,
        message_id=message_id,
        file_id=f"telegram:{chat_id}:{message_id}",
        verified=True
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return {"ok": True, "video_id": video.id}
