from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=True)
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'), nullable=True)
    quality = Column(String(50), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    file_id = Column(String(500), nullable=False)
    duration = Column(Integer, nullable=True)
    resolution = Column(String(20), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    movie = relationship("Movie", back_populates="videos")
    episode = relationship("Episode", back_populates="videos")