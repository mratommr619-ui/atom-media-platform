import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, Boolean
from backend.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"

class UserStatus(str, enum.Enum):
    active = "active"
    banned = "banned"
    muted = "muted"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    language = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    join_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_premium = Column(Boolean, default=False)
    ads_disabled = Column(Boolean, default=False)
    warnings = Column(Integer, default=0)
