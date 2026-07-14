from datetime import datetime
from typing import Optional

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.models.episode import Episode
from backend.models.user import User
from backend.models.video import Video
from backend.models.watch_history import WatchHistory


async def deliver_protected_video(
    *,
    db: AsyncSession,
    telegram_id: int,
    video_id: int,
    bot: Optional[Bot] = None,
) -> None:
    result = await db.execute(
        select(Video)
        .options(
            selectinload(Video.movie),
            selectinload(Video.episode).selectinload(Episode.series),
        )
        .where(Video.id == video_id)
    )
    video = result.scalars().first()
    if not video:
        raise ValueError("Video not found")

    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalars().first()
    if not user:
        raise ValueError("User not found")

    owns_bot = bot is None
    active_bot = bot or Bot(token=settings.BOT_TOKEN)
    try:
        caption = _video_caption(video)
        if video.file_id.startswith("telegram:"):
            await active_bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=video.chat_id,
                message_id=video.message_id,
                protect_content=True,
                caption=caption or None,
            )
        else:
            await active_bot.send_video(
                chat_id=user.telegram_id,
                video=video.file_id,
                protect_content=True,
                caption=caption or None,
            )
    finally:
        if owns_bot:
            await active_bot.session.close()

    series_id = video.episode.series_id if video.episode else None
    history = WatchHistory(
        user_id=user.id,
        movie_id=video.movie_id,
        series_id=series_id,
        episode_id=video.episode_id,
        video_id=video.id,
        watched_at=datetime.utcnow(),
    )
    db.add(history)
    await db.commit()


def _video_caption(video: Video) -> str:
    if video.movie:
        return video.movie.title

    if video.episode and video.episode.series:
        episode_label = f"Episode {video.episode.episode_number}"
        if video.episode.title:
            episode_label = f"{episode_label} - {video.episode.title}"
        return f"{video.episode.series.title}\n{episode_label}"

    return ""
