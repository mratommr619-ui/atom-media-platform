import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models.poll import Poll
from backend.models.user import User

logger = logging.getLogger(__name__)


async def send_poll(poll_id: int) -> None:
    async with AsyncSessionLocal() as session:
        poll = (await session.execute(
            select(Poll).options(selectinload(Poll.options)).where(Poll.id == poll_id)
        )).scalars().first()
        if not poll or poll.is_closed:
            return
        users = (await session.execute(select(User))).scalars().all()
        bot = Bot(token=settings.BOT_TOKEN)
        try:
            for user in users:
                try:
                    await bot.send_poll(
                        chat_id=user.telegram_id,
                        question=poll.question,
                        options=[option.text for option in poll.options],
                        is_anonymous=poll.is_anonymous,
                        allows_multiple_answers=poll.is_multiple_choice,
                    )
                except Exception as error:
                    logger.warning("Poll %s failed for %s: %s", poll_id, user.telegram_id, error)
        finally:
            await bot.session.close()
