from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.movie import movie_keywords
from backend.models.series import series_keywords

class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255), unique=True, nullable=False, index=True)
    
    movies = relationship("Movie", secondary=movie_keywords, back_populates="keywords")
    series = relationship("Series", secondary=series_keywords, back_populates="keywords")