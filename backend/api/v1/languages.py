from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.user import User
from backend.api.v1.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class LanguageUpdate(BaseModel):
    language: str

@router.put("/language")
async def set_language(data: LanguageUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.language not in ("en", "my"):
        raise HTTPException(status_code=400, detail="Unsupported language")
    user.language = data.language
    await db.commit()
    return {"language": user.language}