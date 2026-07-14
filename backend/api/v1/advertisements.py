from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.auth import get_current_admin
from backend.database import get_db
from backend.models.advertisement import Advertisement
from backend.schemas.advertisement import Advertisement as AdvertisementSchema, AdvertisementCreate, AdvertisementUpdate

router = APIRouter()


@router.get("/", response_model=list[AdvertisementSchema])
async def list_advertisements(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    return (await db.execute(select(Advertisement).order_by(Advertisement.created_at.desc()))).scalars().all()


@router.post("/", response_model=AdvertisementSchema)
async def create_advertisement(data: AdvertisementCreate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    ad = Advertisement(**data.dict())
    db.add(ad)
    await db.commit()
    await db.refresh(ad)
    return ad


@router.put("/{ad_id}", response_model=AdvertisementSchema)
async def update_advertisement(ad_id: int, data: AdvertisementUpdate, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    ad = await db.get(Advertisement, ad_id)
    if not ad:
        raise HTTPException(404, "Advertisement not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(ad, key, value)
    await db.commit()
    await db.refresh(ad)
    return ad


@router.delete("/{ad_id}")
async def delete_advertisement(ad_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    ad = await db.get(Advertisement, ad_id)
    if not ad:
        raise HTTPException(404, "Advertisement not found")
    await db.delete(ad)
    await db.commit()
    return {"ok": True}
