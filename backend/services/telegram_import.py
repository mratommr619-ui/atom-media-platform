import re
from typing import Optional
from aiogram import Bot
from backend.config import settings

async def parse_telegram_link(link: str) -> Optional[dict]:
    pattern1 = r"https?://t\.me/c/(\d+)/(\d+)"
    pattern2 = r"https?://t\.me/([^/]+)/(\d+)"
    match = re.match(pattern1, link)
    if match:
        chat_id = int("-100" + match.group(1))
        message_id = int(match.group(2))
        return {"chat_id": chat_id, "message_id": message_id}
    match = re.match(pattern2, link)
    if match:
        username = match.group(1)
        message_id = int(match.group(2))
        bot = Bot(token=settings.BOT_TOKEN)
        try:
            chat = await bot.get_chat(f"@{username}")
            return {"chat_id": chat.id, "message_id": message_id}
        finally:
            await bot.session.close()
    return None

async def get_video_info(chat_id: int, message_id: int) -> Optional[dict]:
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        message = await bot.get_messages(chat_id, message_id)
        if message.video:
            video = message.video
            return {
                "file_id": video.file_id,
                "duration": video.duration,
                "resolution": f"{video.width}x{video.height}",
                "file_size": video.file_size
            }
        elif message.document and message.document.mime_type.startswith("video/"):
            doc = message.document
            return {
                "file_id": doc.file_id,
                "duration": None,
                "resolution": None,
                "file_size": doc.file_size
            }
        return None
    except Exception:
        return None
    finally:
        await bot.session.close()