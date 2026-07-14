from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

class WatchHistory(Base):
    __tablename__ = "watch_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=True)
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'), nullable=True)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='SET NULL'), nullable=True)
    watched_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User")
    movie = relationship("Movie", back_populates="watch_histories")
    series = relationship("Series", back_populates="watch_histories")
    episode = relationship("Episode")
    video = relationship("Video")