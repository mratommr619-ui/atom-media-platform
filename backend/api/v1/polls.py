from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import get_db
from backend.models.poll import Poll, PollOption
from backend.schemas.poll import PollCreate, Poll as PollSchema
from backend.api.v1.auth import get_current_admin
from backend.services.poll_service import send_poll

router = APIRouter()

@router.post("/", response_model=PollSchema)
async def create_poll(poll: PollCreate, background_tasks: BackgroundTasks, db=Depends(get_db), admin=Depends(get_current_admin)):
    obj = Poll(question=poll.question, is_anonymous=poll.is_anonymous, is_multiple_choice=poll.is_multiple_choice, created_by=admin.id)
    for opt in poll.options:
        obj.options.append(PollOption(text=opt.text))
    db.add(obj); await db.commit(); await db.refresh(obj)
    background_tasks.add_task(send_poll, obj.id)
    return (await db.execute(select(Poll).options(selectinload(Poll.options)).where(Poll.id == obj.id))).scalars().first()

@router.get("/", response_model=list[PollSchema])
async def list_polls(db=Depends(get_db), admin=Depends(get_current_admin)):
    res = await db.execute(select(Poll).options(selectinload(Poll.options)).order_by(Poll.created_at.desc()))
    return res.scalars().all()

@router.delete("/{poll_id}")
async def delete_poll(poll_id: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    poll = await db.get(Poll, poll_id)
    if not poll:
        raise HTTPException(404, "Poll not found")
    await db.delete(poll)
    await db.commit()
    return {"ok": True}
