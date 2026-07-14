import asyncio
import logging
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import AsyncSessionLocal
from backend.models.broadcast import Broadcast, BroadcastStatus
from backend.models.user import User
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from backend.config import settings
from typing import List

logger = logging.getLogger(__name__)

async def send_broadcast(broadcast_id: int):
    async with AsyncSessionLocal() as session:
        broadcast = await session.get(Broadcast, broadcast_id)
        if not broadcast or broadcast.status != BroadcastStatus.sending:
            return

        bot = Bot(token=settings.BOT_TOKEN)
        sent, failed = 0, 0
        try:
            broadcast.total_users_count = await session.scalar(select(func.count(User.id))) or 0
            query = select(User)
            if not broadcast.target_all:
                if broadcast.target_user_ids:
                    query = query.where(User.telegram_id.in_(broadcast.target_user_ids))
                if broadcast.target_languages:
                    query = query.where(User.language.in_(broadcast.target_languages))

            users: List[User] = (await session.execute(query)).scalars().all()
            broadcast.target_count = len(users)
            broadcast.sent_count = 0
            broadcast.delivered_count = 0
            broadcast.failed_count = 0
            await session.commit()

            keyboard = None
            if broadcast.buttons:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=btn['text'], url=btn.get('url'), callback_data=btn.get('callback_data'))]
                    for btn in broadcast.buttons
                ])

            for index, user in enumerate(users, start=1):
                try:
                    if broadcast.type == 'text':
                        await bot.send_message(chat_id=user.telegram_id, text=broadcast.content, parse_mode=broadcast.parse_mode, reply_markup=keyboard)
                    elif broadcast.type == 'photo':
                        await bot.send_photo(chat_id=user.telegram_id, photo=broadcast.media_file_id, caption=broadcast.content, parse_mode=broadcast.parse_mode, reply_markup=keyboard)
                    elif broadcast.type == 'video':
                        await bot.send_video(chat_id=user.telegram_id, video=broadcast.media_file_id, caption=broadcast.content, parse_mode=broadcast.parse_mode, reply_markup=keyboard)
                    sent += 1
                except Exception as exc:
                    logger.warning("Broadcast %s failed for %s: %s", broadcast.id, user.telegram_id, exc)
                    failed += 1
                if index % 10 == 0:
                    broadcast.sent_count = sent
                    broadcast.delivered_count = sent
                    broadcast.failed_count = failed
                    await session.commit()

            broadcast.status = BroadcastStatus.sent if sent or not users else BroadcastStatus.failed
        except Exception:
            logger.exception("Broadcast %s stopped unexpectedly", broadcast_id)
            broadcast.status = BroadcastStatus.failed
        finally:
            broadcast.sent_count = sent
            broadcast.delivered_count = sent
            broadcast.failed_count = failed
            broadcast.completed_at = datetime.utcnow()
            await session.commit()
            await bot.session.close()
