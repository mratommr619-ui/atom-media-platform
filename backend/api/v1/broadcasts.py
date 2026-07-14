from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.broadcast import Broadcast
from backend.schemas.broadcast import BroadcastCreate, Broadcast as BroadSchema
from backend.api.v1.auth import get_current_admin
from backend.services.broadcast_service import send_broadcast

router = APIRouter()

@router.post("/", response_model=BroadSchema)
async def create_broadcast(bc: BroadcastCreate, background_tasks: BackgroundTasks, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Broadcast(**bc.dict(), created_by=admin.id, status='sending')
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    background_tasks.add_task(send_broadcast, obj.id)
    return obj

@router.get("/", response_model=list[BroadSchema])
async def list_broadcasts(db=Depends(get_db), admin=Depends(get_current_admin)):
    results = await db.execute(select(Broadcast).order_by(Broadcast.created_at.desc()))
    return results.scalars().all()

@router.delete("/{broadcast_id}")
async def delete_broadcast(broadcast_id: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    item = await db.get(Broadcast, broadcast_id)
    if not item:
        raise HTTPException(404, "Broadcast not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}
