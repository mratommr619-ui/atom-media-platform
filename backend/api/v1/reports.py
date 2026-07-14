from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.report import Report
from backend.schemas.report import Report as RepSchema, ReportUpdate
from backend.api.v1.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=list[RepSchema])
async def list_reports(status: str = None, db=Depends(get_db), admin=Depends(get_current_admin)):
    # Selecting the table returned raw columns, so ``scalars()`` produced an
    # integer instead of a Report object and the response model failed.
    query = select(Report)
    if status:
        query = query.where(Report.status == status)
    res = await db.execute(query.order_by(Report.created_at.desc()))
    return res.scalars().all()

@router.put("/{report_id}", response_model=RepSchema)
async def update_report(report_id: int, update: ReportUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    rep = await db.get(Report, report_id)
    if not rep: raise HTTPException(404)
    for k,v in update.dict(exclude_unset=True).items(): setattr(rep,k,v)
    await db.commit(); await db.refresh(rep); return rep
