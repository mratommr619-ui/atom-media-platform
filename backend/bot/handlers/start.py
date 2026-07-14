from aiogram import F, Router, types
from aiogram.filters import CommandStart
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models.user import User, UserRole
from backend.config import settings
from datetime import datetime
from backend.bot.utils.language import get_text

router = Router()

def _is_configured_admin(telegram_id: int) -> bool:
    admin_ids = set(settings.ADMIN_TELEGRAM_IDS)
    try:
        admin_ids.add(int(settings.ADMIN_CHAT_ID))
    except (TypeError, ValueError):
        pass
    return telegram_id in admin_ids

def _get_main_keyboard(lang: str) -> types.ReplyKeyboardMarkup:
    """Get main keyboard with translated buttons."""
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text=get_text(lang, "btn_search")),
                types.KeyboardButton(text=get_text(lang, "btn_favorites"))
            ],
            [
                types.KeyboardButton(text=get_text(lang, "btn_request")),
                types.KeyboardButton(text=get_text(lang, "btn_report"))
            ],
            [types.KeyboardButton(text=get_text(lang, "btn_language"))],
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user.scalars().first()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language=None,
                role=UserRole.admin if _is_configured_admin(message.from_user.id) else UserRole.user,
                join_date=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            session.add(user)
            await session.commit()
        else:
            if _is_configured_admin(message.from_user.id):
                user.role = UserRole.admin
            user.last_active = datetime.utcnow()
            await session.commit()
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="English", callback_data="lang_en"),
                types.InlineKeyboardButton(text="မြန်မာ", callback_data="lang_mm"),
            ]
        ])
        await message.answer(get_text("en", "choose_language"), reply_markup=keyboard)

def _is_language_button(message: types.Message) -> bool:
    text = (message.text or "").casefold()
    return "language" in text or "ဘာသာ" in text


@router.message(_is_language_button)
async def language_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="English", callback_data="lang_en"),
            types.InlineKeyboardButton(text="မြန်မာ", callback_data="lang_mm"),
        ]
    ])
    await message.answer(get_text("en", "choose_language"), reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    language = callback.data.split("_", 1)[1]
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        user = result.scalars().first()
        if user:
            user.language = language
            user.last_active = datetime.utcnow()
            await session.commit()
    
    # Show confirmation and main menu with translated buttons
    await callback.message.answer(get_text(language, "language_saved"))
    welcome_text = get_text(language, "welcome", name=user.first_name or callback.from_user.first_name)
    await callback.message.answer(
        welcome_text,
        reply_markup=_get_main_keyboard(language)
    )
    await callback.answer()
