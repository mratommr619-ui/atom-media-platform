from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy import select

from backend.bot.handlers.start import _get_main_keyboard
from backend.bot.handlers.search import get_embed_service
from backend.bot.utils.language import get_text
from backend.bot.utils.reply_database import reply_database
from backend.bot.utils.daily_chat import daily_reply, detect_intent, follow_up_reply
from aiogram.fsm.context import FSMContext
from backend.database import AsyncSessionLocal
from backend.models.user import User
from backend.services.search import search_content

router = Router()


async def _user_language(telegram_id: int) -> str:
    async with AsyncSessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalars().first()
        return user.language if user and user.language else "en"


@router.message(Command("help"))
async def help_command(message: types.Message):
    lang = await _user_language(message.from_user.id)
    await message.answer(get_text(lang, "help_text"), reply_markup=_get_main_keyboard(lang))


@router.message(F.text)
async def conversational_fallback(message: types.Message, state: FSMContext):
    lang = await _user_language(message.from_user.id)
    query = (message.text or "").strip()
    if query.startswith("/"):
        await message.answer(get_text(lang, "help_text"), reply_markup=_get_main_keyboard(lang))
        return

    intent = detect_intent(query, lang)
    friendly = daily_reply(query, lang) or _friendly_reply(query, lang)
    if friendly:
        await state.update_data(conversation_intent=intent)
        await message.answer(friendly, reply_markup=_get_main_keyboard(lang))
        return

    previous_intent = (await state.get_data()).get("conversation_intent")
    follow_up = follow_up_reply(query, lang, previous_intent)
    if follow_up:
        await message.answer(follow_up, reply_markup=_get_main_keyboard(lang))
        return

    canned = reply_database.find(query, lang)
    if canned and canned.score >= 0.58:
        await message.answer(canned.answer, reply_markup=_get_main_keyboard(lang))
        return

    # Short everyday messages are conversation, not a movie request.  This
    # keeps greetings and casual Myanmar chat out of the content search path.
    if not _looks_like_content_request(query):
        if canned and canned.score >= 0.34:
            await message.answer(canned.answer, reply_markup=_get_main_keyboard(lang))
        else:
            await message.answer(get_text(lang, "assistant_fallback"), reply_markup=_get_main_keyboard(lang))
        return

    progress = await message.answer(get_text(lang, "searching"))
    async with AsyncSessionLocal() as db:
        items, _ = await search_content(db, query, None, page=1, per_page=5)
    try:
        await progress.delete()
    except Exception:
        pass

    if items:
        text = get_text(lang, "search_results") + "\n\n"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for item in items[:5]:
            label = "Movie" if item.type == "movie" else "Series"
            text += f"{item.title} ({label})\n"
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(
                    text=item.title,
                    callback_data=f"select_{item.type}_{item.id}",
                )
            ])
        await message.answer(text, reply_markup=keyboard)
        return

    if canned and canned.score >= 0.34:
        await message.answer(canned.answer, reply_markup=_get_main_keyboard(lang))
        return

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
    await message.answer(
        get_text(lang, "unknown_answer"),
        reply_markup=keyboard,
    )


def _looks_like_content_request(query: str) -> bool:
    lower = query.casefold()
    content_words = ("movie", "series", "film", "anime", "episode", "ရုပ်ရှင်", "ကား", "ဇာတ်လမ်း", "အပိုင်း", "အာဗာတာ", "အပြာရောင်")
    if any(word in lower for word in content_words):
        return True
    # A one-to-six word Latin title such as Avatar is a reasonable direct
    # lookup. Full sentences and Myanmar chat remain conversational.
    words = lower.split()
    return bool(words) and len(words) <= 6 and lower.isascii() and len(lower) >= 2 and any(char.isalpha() for char in lower)


def _friendly_reply(query: str, lang: str) -> str | None:
    text = query.casefold()
    if any(word in text for word in ("နာမည်", "ဘယ်လိုခေါ်", "your name", "what is your name")):
        return "ကျွန်တော့်နာမည်က Atom ပါ။ အရမ်းချောတယ်လို့တော့ user တွေက ပြောကြပါတယ်။ ရုပ်ရှင်ရှာဖို့လည်း အမြဲအဆင်သင့်ပါ။" if lang == "mm" else "My name is Atom. Some users say I am quite charming, but I am here to find your movie first."
    if any(word in text for word in ("နေကောင်း", "how are you", "နေကောင်းလား")):
        return "Atom က အဆင်ပြေပါတယ်။ သင်ရှာချင်တဲ့ကားနာမည်ပေးလိုက်ရင် အလုပ်ဝင်ဖို့အဆင်သင့်ပါ။" if lang == "mm" else "Atom is doing well and ready to find something good to watch."
    if any(word in text for word in ("ဟာသ", "joke", "ရယ်စရာ")):
        return "ရုပ်ရှင်ရှာတဲ့ Atom က အားမနာဘူး၊ မတွေ့ရင်တောင် Admin ဆီတောင်းပေးဖို့ လမ်းညွှန်ပေးတတ်တယ်။" if lang == "mm" else "Why did Atom bring a search button? Because every good story deserves to be found."
    if any(word in text for word in ("admin", "developer", "ဖန်တီး", "ဘယ်သူလုပ်")):
        return "Atom ကိုလုပ်ထားတဲ့ developer က budget နည်းနည်းနဲ့ feature များများထည့်ဖို့ကြိုးစားနေသူပါ။ User တွေသုံးပေးရင် instant noodle ကို upgrade လုပ်နိုင်မယ်လို့မျှော်လင့်နေပါတယ်။" if lang == "mm" else "Atom was built by a developer trying to fit many features into a small budget. Every happy user helps upgrade the instant-noodle roadmap."
    return None
