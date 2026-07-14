import re

from aiogram import types


async def send_media_card(
    message: types.Message,
    media_url: str | None,
    caption: str,
    reply_markup: types.InlineKeyboardMarkup,
) -> None:
    """Send a poster from a direct URL or copy a Telegram poster message."""
    if media_url:
        telegram_source = await _telegram_source(message.bot, media_url)
        if telegram_source:
            try:
                await message.bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=telegram_source[0],
                    message_id=telegram_source[1],
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                    protect_content=True,
                )
                return
            except Exception:
                pass
        try:
            await message.answer_photo(
                photo=media_url,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
            return
        except Exception:
            pass
    await message.answer(caption, reply_markup=reply_markup, parse_mode="Markdown")


async def _telegram_source(bot, value: str) -> tuple[int, int] | None:
    match = re.match(r"https?://t\.me/c/(\d+)/(\d+)", value)
    if match:
        return int(f"-100{match.group(1)}"), int(match.group(2))
    match = re.match(r"https?://t\.me/([^/?#]+)/([0-9]+)", value)
    if not match:
        return None
    try:
        chat = await bot.get_chat(f"@{match.group(1)}")
        return chat.id, int(match.group(2))
    except Exception:
        return None
