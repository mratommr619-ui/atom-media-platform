"""
Atom Media Platform - Telegram Bot Runner (မြန်မာ / English)
============================================================
ဤ script သည် Telegram Bot ကို FastAPI server မပါဘဲ သီးသန့် run ရန်အတွက်ဖြစ်သည်။
This script runs the Telegram bot independently (without the FastAPI server).

Usage / အသုံးပြုရန်:
    python backend/run_bot.py
    python -m backend.run_bot

Requirements / လိုအပ်ချက်များ:
    - Redis server running (default: redis://localhost:6379/0)
    - PostgreSQL database (configured in .env)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from backend.config import settings
from backend.database import engine, Base
from backend.bot.bot import bot, dp, setup_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    print("=" * 56)
    print("  Atom Media Platform - Telegram Bot")
    print("  အက်တမ်မီဒီယာ - တယ်လီဂရမ်ဘော့တ်")
    print("=" * 56)
    print(f"  EN: Bot Token : {settings.BOT_TOKEN[:8]}...{settings.BOT_TOKEN[-4:]}")
    print(f"  MM: ဘော့တ်သော့ : {settings.BOT_TOKEN[:8]}...{settings.BOT_TOKEN[-4:]}")
    print(f"  EN: Admin ID  : {settings.ADMIN_CHAT_ID}")
    print(f"  MM: အက်ဒမင် ID: {settings.ADMIN_CHAT_ID}")
    print(f"  EN: Mini App  : {settings.MINI_APP_URL}")
    print(f"  MM: မီနီအက်ပ် : {settings.MINI_APP_URL}")
    print(f"  EN: Redis URL : {settings.REDIS_URL}")
    print(f"  MM: Redis လိပ်စာ: {settings.REDIS_URL}")
    print("=" * 56)

    # Try to create database tables (safe if they already exist)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ EN: Database connection OK - tables ensured.")
        logger.info("✓ MM: Database ချိတ်ဆက်မှုအောင်မြင် - ဇယားများအဆင်သင့်ဖြစ်ပြီး။")
    except Exception as e:
        logger.warning(f"⚠ EN: Database connection failed: {e}")
        logger.warning("  EN: Bot will still run but search/watch features may not work.")
        logger.warning("⚠ MM: Database ချိတ်ဆက်မှုမအောင်မြင်")
        logger.warning("  MM: ဘော့တ် run နိုင်သေးသော်လည်း ရှာဖွေခြင်း/ကြည့်ရှုခြင်းများ အလုပ်မလုပ်နိုင်ပါ။")

    if settings.BOT_MODE.casefold() == "webhook":
        logger.info("Webhook mode is enabled; start the FastAPI service instead of polling.")
        return

    # Setup handlers
    setup_handlers()
    router_count = len(dp.sub_routers)
    logger.info(f"✓ EN: {router_count} handlers registered.")
    logger.info(f"✓ MM: {router_count} ခု လုပ်ဆောင်ချက်များ မှတ်ပုံတင်ပြီးပါပြီ။")

    # Start polling
    print("=" * 56)
    print("  EN: Starting bot polling... Press Ctrl+C to stop.")
    print("  MM: ဘော့တ် စတင်နေပါပြီ... ရပ်ရန် Ctrl+C နှိပ်ပါ။")
    print("=" * 56)
    
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"✗ EN: Bot polling failed: {e}")
        logger.error(f"✗ MM: ဘော့တ် စတင်မှု မအောင်မြင်: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n")
        print("=" * 56)
        print("  EN: Bot stopped by user.")
        print("  MM: ဘော့တ်အား အသုံးပြုသူမှ ရပ်ဆိုင်းလိုက်ပါသည်။")
        print("=" * 56)
