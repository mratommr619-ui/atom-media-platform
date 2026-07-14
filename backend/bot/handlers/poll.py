from aiogram import Router, types, F
from aiogram.filters import Command
from backend.database import AsyncSessionLocal
from backend.models.poll import Poll, PollOption, Vote
from backend.models.user import User
from sqlalchemy import select
from backend.bot.utils.language import get_text

router = Router()

@router.message(Command("polls"))
async def list_polls(message: types.Message):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == message.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Poll).where(Poll.is_closed == False))
        polls = result.scalars().all()
        if not polls:
            await message.answer(get_text(lang, "no_active_polls"))
            return
        for poll in polls:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=opt.text, callback_data=f"vote_{poll.id}_{opt.id}")]
                for opt in poll.options
            ])
            await message.answer(f"{get_text(lang, 'poll_question')} {poll.question}", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("vote_"))
async def process_vote(callback: types.CallbackQuery):
    # Get user language
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalars().first()
        lang = user.language if user else "en"
    
    parts = callback.data.split("_")
    poll_id = int(parts[1])
    option_id = int(parts[2])
    user = callback.from_user
    async with AsyncSessionLocal() as session:
        poll = await session.get(Poll, poll_id)
        if not poll or poll.is_closed:
            await callback.answer(get_text(lang, "poll_closed"))
            return
        # Check if user already voted (if not multiple choice)
        existing = await session.execute(select(Vote).where(Vote.poll_id == poll_id, Vote.user_id == user.id))
        if not poll.is_multiple_choice and existing.scalars().first():
            await callback.answer(get_text(lang, "already_voted"))
            return
        vote = Vote(poll_id=poll_id, user_id=user.id, option_id=option_id)
        session.add(vote)
        # Update count
        option = await session.get(PollOption, option_id)
        option.vote_count += 1
        await session.commit()
        await callback.answer(get_text(lang, "vote_recorded"))
