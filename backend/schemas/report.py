from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.models.report import ReportType, ReportStatus

class ReportBase(BaseModel):
    movie_id: Optional[int] = None
    series_id: Optional[int] = None
    episode_id: Optional[int] = None
    report_type: ReportType
    description: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    admin_response: Optional[str] = None

class Report(ReportBase):
    id: int
    user_id: int
    status: ReportStatus
    admin_response: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
