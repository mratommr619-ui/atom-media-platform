from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from backend.config import settings
from backend.bot.handlers import start, search, movie, series, watch, favorites, report, poll, request_movie, episode, help
from backend.database import AsyncSessionLocal
import asyncio
import logging

logger = logging.getLogger(__name__)

# Try Redis first, fall back to in-memory storage
storage = MemoryStorage()
try:
    from aiogram.fsm.storage.redis import RedisStorage
    # Test if Redis is actually reachable (non-blocking)
    import socket
    host, port_part = settings.REDIS_URL.replace("redis://", "").split("/")[0].split(":")
    port = int(port_part) if port_part else 6379
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        storage = RedisStorage.from_url(settings.REDIS_URL)
        logger.info("Using Redis storage for FSM")
    else:
        logger.warning(f"Redis at {host}:{port} not reachable, using in-memory storage")
except Exception:
    logger.warning("Redis not available, using in-memory storage (bot state lost on restart)")

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=storage)
_handlers_ready = False

def setup_handlers():
    global _handlers_ready
    if _handlers_ready:
        return
    dp.include_router(start.router)
    dp.include_router(search.router)
    dp.include_router(movie.router)
    dp.include_router(series.router)
    dp.include_router(episode.router)
    dp.include_router(watch.router)
    dp.include_router(favorites.router)
    dp.include_router(report.router)
    dp.include_router(poll.router)
    dp.include_router(request_movie.router)
    dp.include_router(help.router)
    _handlers_ready = True


async def configure_webhook() -> None:
    """Register Telegram delivery to the public API service."""
    setup_handlers()
    base_url = (settings.WEBHOOK_BASE_URL or "").rstrip("/")
    if not base_url or not settings.WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_BASE_URL and WEBHOOK_SECRET are required for webhook mode")
    await bot.set_webhook(
        url=f"{base_url}/telegram/webhook/{settings.WEBHOOK_SECRET}",
        secret_token=settings.WEBHOOK_SECRET,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=False,
    )

async def setup_bot():
    setup_handlers()
    asyncio.create_task(dp.start_polling(bot))

async def shutdown_bot():
    await bot.session.close()
