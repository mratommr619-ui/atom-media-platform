from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from backend.models.broadcast import BroadcastType, BroadcastStatus

class BroadcastBase(BaseModel):
    type: BroadcastType
    content: str
    media_file_id: Optional[str] = None
    buttons: Optional[Any] = None
    parse_mode: str = "HTML"
    target_all: bool = True
    target_languages: Optional[List[str]] = None
    target_user_ids: Optional[List[int]] = None

class BroadcastCreate(BroadcastBase):
    pass

class BroadcastUpdate(BaseModel):
    status: Optional[BroadcastStatus] = None

class Broadcast(BroadcastBase):
    id: int
    status: BroadcastStatus
    total_users_count: int
    target_count: int
    sent_count: int
    delivered_count: int
    failed_count: int
    created_by: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
