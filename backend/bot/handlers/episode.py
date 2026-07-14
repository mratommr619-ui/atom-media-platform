from aiogram import Router, types
from backend.database import AsyncSessionLocal
from backend.models.episode import Episode
from backend.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.bot.utils.language import get_text

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("ep_"))
async def show_episode(callback: types.CallbackQuery):
    ep_id = int(callback.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        # Get user language
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user else "en"
        
        result = await session.execute(
            select(Episode)
            .options(selectinload(Episode.series), selectinload(Episode.videos))
            .where(Episode.id == ep_id)
        )
        episode = result.scalars().first()
        if not episode:
            await callback.answer(get_text(lang, "episode_not_found"))
            return
        series = episode.series
        text = f"📺 {series.title} - {get_text(lang, 'episode')} {episode.episode_number}\n"
        if episode.title: text += f"Title: {episode.title}\n"
        qualities = []
        for v in episode.videos:
            qualities.append(f"{v.quality} • {v.file_size/1e9:.1f} GB" if v.file_size else v.quality)
        if qualities:
            text += "\nQualities:\n" + "\n".join(qualities)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for v in episode.videos:
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=f"{v.quality}", callback_data=f"watch_ep_{episode.id}_{v.id}")])
        await callback.message.answer(text, reply_markup=keyboard)
        # Visual feedback
        await callback.answer("⏳")
