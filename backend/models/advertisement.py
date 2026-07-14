from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database import Base
import datetime

class Advertisement(Base):
    __tablename__ = "advertisements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    media_url = Column(String(500), nullable=True)
    link = Column(String(500), nullable=True)
    duration = Column(Integer, default=15)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)