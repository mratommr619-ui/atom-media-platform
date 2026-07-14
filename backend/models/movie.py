from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime

movie_genres = Table('movie_genres', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE')),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'))
)

movie_keywords = Table('movie_keywords', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE')),
    Column('keyword_id', Integer, ForeignKey('keywords.id', ondelete='CASCADE'))
)

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_mm = Column(String(500), nullable=True)
    description_en = Column(Text, nullable=True)
    description_mm = Column(Text, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True)
    language_original = Column(String(100), nullable=True)
    duration = Column(Integer, nullable=True)
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    keywords = relationship("Keyword", secondary=movie_keywords, back_populates="movies")
    aliases = relationship("Alias", back_populates="movie", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="movie", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="movie", cascade="all, delete-orphan")
    watch_histories = relationship("WatchHistory", back_populates="movie", cascade="all, delete-orphan")