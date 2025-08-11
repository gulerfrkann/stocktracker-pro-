"""
Authentication-related Pydantic schemas
"""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    user_uuid: str
    email: str
    username: str
    full_name: str
    department: str
    role: str
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


