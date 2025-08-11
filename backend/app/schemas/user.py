"""
User-related Pydantic schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    user_uuid: str
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str
    is_verified: bool
    notification_preferences: Optional[Dict[str, Any]] = None
    timezone: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True


