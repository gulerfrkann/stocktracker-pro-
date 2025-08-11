"""
Base model class with common fields
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base


class BaseModel(Base):
    """
    Base model with common fields for all tables
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    @declared_attr
    def __tablename__(cls):
        # Automatically generate table name from class name
        return cls.__name__.lower() + 's'


