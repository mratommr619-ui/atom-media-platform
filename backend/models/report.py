from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime
import enum

class ReportType(str, enum.Enum):
    broken_video = "broken_video"
    wrong_subtitle = "wrong_subtitle"
    wrong_episode = "wrong_episode"
    quality_problem = "quality_problem"
    other = "other"

class ReportStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"
    closed = "closed"
    archived = "archived"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=True)
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'), nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.open)
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User")
    movie = relationship("Movie")
    series = relationship("Series")
    episode = relationship("Episode")