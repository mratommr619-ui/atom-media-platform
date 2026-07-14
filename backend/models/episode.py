from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    series = relationship("Series", back_populates="episodes")
    videos = relationship("Video", back_populates="episode", cascade="all, delete-orphan")