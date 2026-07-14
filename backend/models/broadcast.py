from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime
import enum

class BroadcastType(str, enum.Enum):
    text = "text"
    photo = "photo"
    video = "video"

class BroadcastStatus(str, enum.Enum):
    draft = "draft"
    sending = "sending"
    sent = "sent"
    failed = "failed"

class Broadcast(Base):
    __tablename__ = "broadcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(BroadcastType), nullable=False)
    content = Column(Text, nullable=False)
    media_file_id = Column(String(500), nullable=True)
    buttons = Column(JSON, nullable=True)
    parse_mode = Column(String(20), default="HTML")
    target_all = Column(Boolean, default=True)
    target_languages = Column(JSON, nullable=True)
    target_user_ids = Column(JSON, nullable=True)
    status = Column(Enum(BroadcastStatus), default=BroadcastStatus.draft)
    total_users_count = Column(Integer, default=0)
    target_count = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    creator = relationship("User")

