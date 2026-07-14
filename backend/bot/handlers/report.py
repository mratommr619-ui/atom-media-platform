from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from backend.database import AsyncSessionLocal
from backend.models.report import Report
from backend.models.user import User
from sqlalchemy import select
from backend.bot.utils.language import get_text

router = Router()

class ReportState(StatesGroup):
    waiting_type = State()
    waiting_description = State()

def _is_report_button(message: types.Message) -> bool:
    text = (message.text or "").casefold()
    return "report" in text or "ပြဿနာ" in text or "ကြည့်မရ" in text


@router.message(_is_report_button)
async def start_report(message: types.Message, state: FSMContext):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=get_text(lang, "rep_broken_video"), callback_data="rep_broken_video")],
        [types.InlineKeyboardButton(text=get_text(lang, "rep_wrong_subtitle"), callback_data="rep_wrong_subtitle")],
        [types.InlineKeyboardButton(text=get_text(lang, "rep_wrong_episode"), callback_data="rep_wrong_episode")],
        [types.InlineKeyboardButton(text=get_text(lang, "rep_quality_problem"), callback_data="rep_quality_problem")],
        [types.InlineKeyboardButton(text=get_text(lang, "rep_other"), callback_data="rep_other")],
    ])
    await message.answer(get_text(lang, "report_prompt"), reply_markup=keyboard)
    await state.set_state(ReportState.waiting_type)

@router.callback_query(ReportState.waiting_type)
async def process_type(callback: types.CallbackQuery, state: FSMContext):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    rtype = callback.data.replace("rep_", "")
    await state.update_data(report_type=rtype)
    await callback.message.answer(get_text(lang, "report_desc_prompt"))
    await state.set_state(ReportState.waiting_description)
    await callback.answer()

@router.message(ReportState.waiting_description)
async def process_description(message: types.Message, state: FSMContext):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        report = Report(user_id=user.id, report_type=data['report_type'], description=message.text)
        session.add(report)
        await session.commit()
    await message.answer(get_text(lang, "report_thanks"))
    await state.clear()
