"""Simple test to verify bot imports work - without connecting to DB."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("Testing imports...")

# Don't import database module (which triggers engine creation)
from backend.config import settings
print(f"✓ Config loaded: {settings.PROJECT_NAME}")

# Import bot directly without triggering heavy side-effects
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
print(f"✓ Bot created with token: {settings.BOT_TOKEN[:8]}...")

# Import and register handlers
from backend.bot.handlers import start, search, movie, series, watch, favorites, report, poll, request_movie, episode

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

print(f"✓ All {len(dp._sub_routers)} handlers registered successfully!")

from backend.models.user import User, UserRole
print(f"✓ User model loaded")

print("\n✅ All imports successful!")
print("Ready to start bot with: python backend/run_bot.py")
print("(Make sure PostgreSQL and Redis are running)")