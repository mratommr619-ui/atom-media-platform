from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Atom Media Platform"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "change-me-in-production-use-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    DATABASE_URL: str = "postgresql+asyncpg://atom_user:atom_pass@db:5432/atom_db"
    
    REDIS_URL: str = "redis://redis:6379/0"
    
    BOT_TOKEN: str = "YOUR_BOT_TOKEN"
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    MINI_APP_URL: str = "https://your-mini-app.web.app"
    ADMIN_CHAT_ID: str = "your-admin-chat-id"
    ADMIN_TELEGRAM_IDS: List[int] = []
    ADMIN_PASSWORD: str = "253619Aunthtoonaung"
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    AD_DURATION_SECONDS: int = 15

    # polling is for Docker/VPS.  Render uses a public webhook so one free web
    # service can host both the API and the Telegram bot.
    BOT_MODE: str = "polling"
    WEBHOOK_BASE_URL: Optional[str] = None
    WEBHOOK_SECRET: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Render supplies postgres:// / postgresql:// URLs while SQLAlchemy's
        # async engine requires the asyncpg driver prefix.
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgresql://")
        return value
    
    class Config:
        env_file = ".env"

settings = Settings()
