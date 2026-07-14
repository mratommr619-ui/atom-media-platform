from aiogram import F, Router, types
from backend.database import AsyncSessionLocal
from backend.models.favorite import Favorite
from backend.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.bot.utils.language import get_text

router = Router()

def _is_favorites_button(message: types.Message) -> bool:
    text = (message.text or "").casefold()
    return "favorite" in text or "ကြိုက်" in text


@router.message(_is_favorites_button)
async def list_favorites(message: types.Message):
    # Get user language
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user_result.scalars().first()
        lang = user.language if user else "en"
    
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user_result.scalars().first()
        if not user:
            await message.answer("Please press /start first.")
            return

        result = await session.execute(
            select(Favorite)
            .options(selectinload(Favorite.movie), selectinload(Favorite.series))
            .where(Favorite.user_id == user.id)
            .order_by(Favorite.created_at.desc())
            .limit(20)
        )
        favorites = result.scalars().all()

    if not favorites:
        await message.answer(get_text(lang, "favorites_empty"))
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
    lines = [get_text(lang, "fav_list_title")]
    for favorite in favorites:
        if favorite.movie:
            lines.append(f"{get_text(lang, 'fav_movie_label')} {favorite.movie.title}")
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(text=favorite.movie.title, callback_data=f"select_movie_{favorite.movie.id}")
            ])
        elif favorite.series:
            lines.append(f"{get_text(lang, 'fav_series_label')} {favorite.series.title}")
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(text=favorite.series.title, callback_data=f"select_series_{favorite.series.id}")
            ])
    await message.answer("\n".join(lines), reply_markup=keyboard)

@router.callback_query(lambda c: c.data and (c.data.startswith("fav_movie_") or c.data.startswith("fav_series_")))
async def toggle_favorite(callback: types.CallbackQuery):
    # Get user language
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = user_result.scalars().first()
        lang = user.language if user else "en"
    
    data = callback.data
    if "movie" in data:
        movie_id = int(data.split("_")[2])
        item_type = "movie"
    else:
        series_id = int(data.split("_")[2])
        item_type = "series"
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = user_result.scalars().first()
        if not user:
            await callback.answer("User not found.")
            return
        if item_type == "movie":
            fav = await session.execute(select(Favorite).where(Favorite.user_id==user.id, Favorite.movie_id==movie_id))
        else:
            fav = await session.execute(select(Favorite).where(Favorite.user_id==user.id, Favorite.series_id==series_id))
        fav = fav.scalars().first()
        if fav:
            await session.delete(fav)
            await callback.answer(f"✅ {get_text(lang, 'fav_removed')}")
        else:
            fav = Favorite(user_id=user.id, movie_id=movie_id if item_type=="movie" else None, series_id=series_id if item_type=="series" else None)
            session.add(fav)
            await callback.answer(f"✅ {get_text(lang, 'fav_added')}")
        await session.commit()
