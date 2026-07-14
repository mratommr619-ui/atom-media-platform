from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.movie import movie_genres
from backend.models.series import series_genres

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")
    series = relationship("Series", secondary=series_genres, back_populates="genres")