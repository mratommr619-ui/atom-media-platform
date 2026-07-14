from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import settings
from backend.database import engine, Base
from backend.api.v1.router import api_router
import redis.asyncio as aioredis
from sqlalchemy import text
from backend.bot.bot import bot, configure_webhook, dp, setup_handlers
from aiogram.types import Update

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    # Search uses indexed metadata and aliases in the request path.  Keeping a
    # transformer out of startup prevents cold-host delays and failed health checks.
    app.state.embedding_service = None
    # Create tables (in production use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # These indexes keep title/typo search responsive as the catalogue
        # grows.  They are harmlessly skipped for non-PostgreSQL local tests.
        if conn.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_movies_title_trgm ON movies USING gin (title gin_trgm_ops)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_movies_title_mm_trgm ON movies USING gin (title_mm gin_trgm_ops)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_series_title_trgm ON series USING gin (title gin_trgm_ops)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_series_title_mm_trgm ON series USING gin (title_mm gin_trgm_ops)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_aliases_name_trgm ON aliases USING gin (name gin_trgm_ops)"))
    setup_handlers()
    if settings.BOT_MODE.casefold() == "webhook":
        await configure_webhook()
    yield
    # Shutdown
    await app.state.redis.close()
    await engine.dispose()
    await bot.session.close()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Atom Media Platform API"}


@app.get("/health")
async def health():
    return {"status": "ok", "bot_mode": settings.BOT_MODE}


@app.post("/telegram/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    if secret != settings.WEBHOOK_SECRET or x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
