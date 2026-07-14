from aiogram import Router, types
from backend.database import AsyncSessionLocal
from backend.models.movie import Movie
from backend.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.bot.utils.language import get_text
from backend.bot.utils.media_card import send_media_card

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("select_movie_"))
async def show_movie(callback: types.CallbackQuery):
    movie_id = int(callback.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        # Get user language
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user else "en"
        
        result = await session.execute(
            select(Movie).options(selectinload(Movie.videos)).where(Movie.id == movie_id)
        )
        movie = result.scalars().first()
        if not movie:
            await callback.answer(get_text(lang, "movie_not_found"))
            return
        text = f"🎬 *{movie.title}*\n"
        if movie.year: text += f"Year: {movie.year}\n"
        # Use description based on language
        if lang == "mm" and movie.description_mm:
            text += f"Description: {movie.description_mm}\n"
        elif movie.description_en:
            text += f"Description: {movie.description_en}\n"
        qualities = []
        for v in movie.videos:
            qualities.append(f"{v.quality} • {v.file_size/1e9:.1f} GB" if v.file_size else v.quality)
        if qualities:
            text += "\nAvailable qualities:\n" + "\n".join(qualities)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for v in movie.videos:
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=f"{v.quality}", callback_data=f"watch_movie_{movie.id}_{v.id}")])
        keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=get_text(lang, "btn_add_fav"), callback_data=f"fav_movie_{movie.id}")])
        await send_media_card(callback.message, movie.thumbnail, text, keyboard)
    # Visual feedback
    await callback.answer("⏳")
