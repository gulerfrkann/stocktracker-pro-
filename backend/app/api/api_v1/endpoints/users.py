"""
User management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """
    Get current user profile
    """
    # TODO: Implement current user logic
    # This is a placeholder
    raise HTTPException(status_code=501, detail="Not implemented yet")


