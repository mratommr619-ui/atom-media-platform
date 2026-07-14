from aiogram import Router, types
from redis.asyncio import Redis
from sqlalchemy import select
from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models.user import User
from backend.services.video_delivery import deliver_protected_video
from backend.bot.utils.language import get_text

router = Router()

@router.callback_query(lambda c: c.data and (c.data.startswith("watch_movie_") or c.data.startswith("watch_ep_")))
async def start_watch(callback: types.CallbackQuery):
    data = callback.data
    if data.startswith("watch_movie_"):
        parts = data.split("_")
        movie_id = int(parts[2])
        video_id = int(parts[3])
        content_type = "movie"
        content_id = movie_id
    else:
        parts = data.split("_")
        ep_id = int(parts[2])
        video_id = int(parts[3])
        content_type = "episode"
        content_id = ep_id

    # Get user language
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = result.scalars().first()
        lang = user.language if user else "en"
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = result.scalars().first()
        if user and user.ads_disabled:
            await deliver_protected_video(
                db=session,
                telegram_id=callback.from_user.id,
                video_id=video_id,
                bot=callback.bot,
            )
            await callback.message.answer(get_text(lang, "ads_disabled_msg"))
            await callback.answer("✅")
            return

    token = f"{callback.from_user.id}_{video_id}"
    redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        await redis.setex(f"watch:{token}", 300, "pending")
    finally:
        await redis.aclose()
    webapp_url = f"{settings.MINI_APP_URL}?token={token}&type={content_type}&id={content_id}&video={video_id}"
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="▶️ Watch Now (Ad)", web_app=types.WebAppInfo(url=webapp_url))]
    ])
    await callback.message.answer(get_text(lang, "watch_prompt"), reply_markup=keyboard)
    await callback.answer("⏳")
