"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Token, UserLogin, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    """
    # TODO: Implement authentication logic
    # This is a placeholder implementation
    
    if form_data.username == "admin" and form_data.password == "admin":
        return Token(
            access_token="dummy_token",
            token_type="bearer"
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout():
    """
    User logout endpoint
    """
    return {"message": "Successfully logged out"}


