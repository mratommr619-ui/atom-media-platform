from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User")
    movie = relationship("Movie", back_populates="favorites")
    series = relationship("Series", back_populates="favorites")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),
        UniqueConstraint('user_id', 'series_id', name='_user_series_uc'),
    )