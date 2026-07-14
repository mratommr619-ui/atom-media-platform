from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PollOptionBase(BaseModel):
    text: str

class PollOptionCreate(PollOptionBase):
    pass

class PollOption(PollOptionBase):
    id: int
    vote_count: int

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    option_id: int

class Vote(VoteBase):
    id: int
    poll_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PollBase(BaseModel):
    question: str
    is_anonymous: bool = True
    is_multiple_choice: bool = False
    is_closed: bool = False
    options: List[PollOptionCreate]

class PollCreate(PollBase):
    pass

class PollUpdate(BaseModel):
    question: Optional[str] = None
    is_closed: Optional[bool] = None

class Poll(PollBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    closed_at: Optional[datetime]
    options: List[PollOption] = []

    class Config:
        from_attributes = True
