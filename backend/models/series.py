from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

series_genres = Table('series_genres', Base.metadata,
    Column('series_id', Integer, ForeignKey('series.id', ondelete='CASCADE')),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'))
)

series_keywords = Table('series_keywords', Base.metadata,
    Column('series_id', Integer, ForeignKey('series.id', ondelete='CASCADE')),
    Column('keyword_id', Integer, ForeignKey('keywords.id', ondelete='CASCADE'))
)

class Series(Base):
    __tablename__ = "series"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_mm = Column(String(500), nullable=True)
    description_en = Column(Text, nullable=True)
    description_mm = Column(Text, nullable=True)
    poster = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True)
    language_original = Column(String(100), nullable=True)
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    episodes = relationship("Episode", back_populates="series", cascade="all, delete-orphan", order_by="Episode.episode_number")
    genres = relationship("Genre", secondary=series_genres, back_populates="series")
    keywords = relationship("Keyword", secondary=series_keywords, back_populates="series")
    aliases = relationship("Alias", back_populates="series", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="series", cascade="all, delete-orphan")
    watch_histories = relationship("WatchHistory", back_populates="series", cascade="all, delete-orphan")