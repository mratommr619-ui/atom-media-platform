from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from backend.services.search import search_content
from backend.database import AsyncSessionLocal
from backend.models.user import User
from sqlalchemy import select
from backend.bot.utils.language import get_text

router = Router()

# Lazy initialization - embedding model is heavy to load
_embed_service = None
def get_embed_service():
    global _embed_service
    if _embed_service is None:
        from backend.services.embedding import EmbeddingService
        _embed_service = EmbeddingService()
    return _embed_service

class SearchState(StatesGroup):
    waiting_query = State()

def _is_search_button(message: types.Message) -> bool:
    text = (message.text or "").casefold()
    return "search" in text or "ရှာ" in text


@router.message(_is_search_button)
async def search_prompt(message: types.Message, state: FSMContext):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    await message.answer(get_text(lang, "search_prompt"))
    await state.set_state(SearchState.waiting_query)

@router.message(SearchState.waiting_query)
async def do_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    if len("".join(query.split())) < 2:
        await message.answer(
            "အနည်းဆုံး စာလုံး ၂ လုံး (သို့) ကားနာမည်ပိုရှင်းရှင်းရေးပေးပါ။" if lang == "mm" else "Please enter at least two characters or a clearer title.",
        )
        return

    async with AsyncSessionLocal() as db:
        progress = await message.answer(get_text(lang, "searching"))
        items, total = await search_content(db, query, None, page=1, per_page=10)
        try:
            await progress.delete()
        except Exception:
            pass
        if not items:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=get_text(lang, "btn_request_this"),
                            callback_data="request_missing",
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text=get_text(lang, "btn_contact_admin"),
                            url="https://t.me/mratom_619",
                        )
                    ],
                ]
            )
            await message.answer(get_text(lang, "no_results"), reply_markup=keyboard)
        else:
            text = get_text(lang, "search_results") + "\n\n"
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
            for item in items[:5]:
                emoji = "🎬" if item.type == "movie" else "📺"
                text += f"{emoji} {item.title} ({item.type.capitalize()})\n"
                callback_data = f"select_{item.type}_{item.id}"
                keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=f"{item.title}", callback_data=callback_data)])
            await message.answer(text, reply_markup=keyboard)
    await state.clear()
