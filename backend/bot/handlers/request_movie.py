from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from backend.database import AsyncSessionLocal
from backend.models.user import User
from sqlalchemy import select
from backend.bot.utils.language import get_text

router = Router()

class RequestState(StatesGroup):
    waiting_title = State()

def _is_request_button(message: types.Message) -> bool:
    text = (message.text or "").casefold()
    return "request" in text or "တောင်း" in text


@router.message(_is_request_button)
async def start_request(message: types.Message, state: FSMContext):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    await message.answer(get_text(lang, "request_prompt"))
    await state.set_state(RequestState.waiting_title)


@router.callback_query(F.data == "request_missing")
async def start_missing_request(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user and user.language else "en"

    await callback.message.answer(get_text(lang, "request_prompt"))
    await callback.answer()
    await state.set_state(RequestState.waiting_title)

@router.message(RequestState.waiting_title)
async def receive_request(message: types.Message, state: FSMContext):
    title = (message.text or message.caption or "").strip()
    
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    from backend.config import settings
    caption = f"New content request from {message.from_user.full_name} (@{message.from_user.username}): {title or 'Poster only'}"
    if message.photo:
        await message.bot.send_photo(chat_id=settings.ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=caption)
    else:
        await message.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=caption)
    await message.answer(get_text(lang, "request_sent"))
    await state.clear()
