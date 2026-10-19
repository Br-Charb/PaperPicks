from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="member", nullable=False) # Either member or admin
    balance = Column(Float, default=1000.0, nullable=False)  
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)