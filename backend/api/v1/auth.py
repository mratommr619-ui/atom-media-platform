import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.setting import Setting
from backend.models.user import User as UserModel, UserRole
from backend.schemas.user import User
from backend.schemas.token import Token
from backend.services.auth import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from backend.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class LoginRequest(BaseModel):
    telegram_id: int | None = None
    password: str | None = None
    device_id: str | None = None
    device_name: str | None = None

class AdminDevice(BaseModel):
    device_id: str
    device_name: str | None = None
    approved: bool = False

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserModel:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await db.get(UserModel, payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role not in ("admin", "moderator"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    if request.password is not None:
        if request.password != settings.ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid admin password")
        if request.device_id:
            await _ensure_device_allowed(db, request.device_id, request.device_name)
        telegram_id = request.telegram_id or _primary_admin_telegram_id()
        user = await _get_or_create_admin(db, telegram_id)
        token = create_access_token(data={"sub": user.id, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}

    if request.telegram_id is None:
        raise HTTPException(status_code=422, detail="telegram_id or password is required")

    user = await db.execute(select(UserModel).where(UserModel.telegram_id == request.telegram_id))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not registered via bot")
    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.get("/admin-devices", response_model=list[AdminDevice])
async def list_admin_devices(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    approved = await _load_setting_json(db, "approved_admin_devices", [])
    pending = await _load_setting_json(db, "pending_admin_devices", [])
    devices = [AdminDevice(**item, approved=True) for item in approved]
    devices.extend(AdminDevice(**item, approved=False) for item in pending)
    return devices

@router.post("/admin-devices/{device_id}/approve")
async def approve_admin_device(device_id: str, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    approved = await _load_setting_json(db, "approved_admin_devices", [])
    pending = await _load_setting_json(db, "pending_admin_devices", [])
    match = next((item for item in pending if item["device_id"] == device_id), {"device_id": device_id, "device_name": None})
    pending = [item for item in pending if item["device_id"] != device_id]
    if not any(item["device_id"] == device_id for item in approved):
        approved.append(match)
    await _save_setting_json(db, "approved_admin_devices", approved)
    await _save_setting_json(db, "pending_admin_devices", pending)
    await db.commit()
    return {"ok": True}

def _primary_admin_telegram_id() -> int:
    if settings.ADMIN_TELEGRAM_IDS:
        return int(settings.ADMIN_TELEGRAM_IDS[0])
    try:
        return int(settings.ADMIN_CHAT_ID)
    except (TypeError, ValueError):
        return 0

async def _get_or_create_admin(db: AsyncSession, telegram_id: int) -> UserModel:
    result = await db.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        user = UserModel(
            telegram_id=telegram_id,
            username="admin",
            first_name="Admin",
            last_name=None,
            language="mm",
            role=UserRole.admin,
            join_date=datetime.utcnow(),
            last_active=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    user.role = UserRole.admin
    user.last_active = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user

async def _ensure_device_allowed(db: AsyncSession, device_id: str, device_name: str | None) -> None:
    approved = await _load_setting_json(db, "approved_admin_devices", [])
    pending = await _load_setting_json(db, "pending_admin_devices", [])
    if not approved:
        approved.append({"device_id": device_id, "device_name": device_name})
        await _save_setting_json(db, "approved_admin_devices", approved)
        await db.commit()
        return
    if any(item["device_id"] == device_id for item in approved):
        return
    if not any(item["device_id"] == device_id for item in pending):
        pending.append({"device_id": device_id, "device_name": device_name})
        await _save_setting_json(db, "pending_admin_devices", pending)
        await db.commit()
    raise HTTPException(status_code=403, detail="This device is waiting for admin approval")

async def _load_setting_json(db: AsyncSession, key: str, default):
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalars().first()
    if not setting or not setting.value:
        return default
    try:
        return json.loads(setting.value)
    except json.JSONDecodeError:
        return default

async def _save_setting_json(db: AsyncSession, key: str, value) -> None:
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalars().first()
    if not setting:
        setting = Setting(key=key, value_type="json", description=key)
        db.add(setting)
    setting.value = json.dumps(value)
