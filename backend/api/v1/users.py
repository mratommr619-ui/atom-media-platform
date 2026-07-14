from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import User as UserSchema, UserUpdate
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=list[UserSchema])
async def list_users(page:int=1, per_page:int=50, search:str=None, db=Depends(get_db), admin=Depends(get_current_admin)):
    query = select(User)
    if search:
        query = query.where(or_(User.first_name.ilike(f"%{search}%"), User.username.ilike(f"%{search}%")))
    query = query.offset((page-1)*per_page).limit(per_page)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(user_id:int, update:UserUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    for k,v in update.dict(exclude_unset=True).items(): setattr(user,k,v)
    await db.commit(); await db.refresh(user); return user

@router.post("/{user_id}/ban")
async def ban_user(user_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    user.status = "banned"; await db.commit()
    return {"ok":True}

@router.post("/{user_id}/unban")
async def unban_user(user_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    user.status = "active"; await db.commit()
    return {"ok":True}

@router.post("/{user_id}/ads/disable", response_model=UserSchema)
async def disable_ads(user_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    user.ads_disabled = True
    await db.commit(); await db.refresh(user)
    return user

@router.post("/{user_id}/ads/enable", response_model=UserSchema)
async def enable_ads(user_id:int, db=Depends(get_db), admin=Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user: raise HTTPException(404)
    user.ads_disabled = False
    await db.commit(); await db.refresh(user)
    return user
