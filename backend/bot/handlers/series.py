from aiogram import Router, types
from backend.database import AsyncSessionLocal
from backend.models.series import Series
from backend.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.bot.utils.language import get_text
from backend.bot.utils.media_card import send_media_card

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("select_series_"))
async def show_series(callback: types.CallbackQuery):
    series_id = int(callback.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        # Get user language
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user else "en"
        
        result = await session.execute(
            select(Series).options(selectinload(Series.episodes)).where(Series.id == series_id)
        )
        series = result.scalars().first()
        if not series:
            await callback.answer(get_text(lang, "series_not_found"))
            return
        text = f"📺 *{series.title}*\n"
        if series.year: text += f"Year: {series.year}\n"
        # Use description based on language
        if lang == "mm" and series.description_mm:
            text += f"Description: {series.description_mm}\n"
        elif series.description_en:
            text += f"Description: {series.description_en}\n"
        text += f"\nEpisodes: {len(series.episodes)}"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for ep in series.episodes:
            btn = types.InlineKeyboardButton(text=f"Ep {ep.episode_number}: {ep.title or 'No title'}", callback_data=f"ep_{ep.id}")
            keyboard.inline_keyboard.append([btn])
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=get_text(lang, "btn_add_fav"), callback_data=f"fav_series_{series.id}")])
        await send_media_card(callback.message, series.poster, text, keyboard)
    # Visual feedback
    await callback.answer("⏳")
