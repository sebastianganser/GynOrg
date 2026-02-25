"""
Authentication endpoints for GynOrg API.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    Token,
    LoginRequest
)
from app.core.config import settings

router = APIRouter()
basic_auth = HTTPBasic()

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Login endpoint that accepts username/password and returns JWT token.
    """
    if not authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """
    Logout endpoint (JWT tokens are stateless, so this is mainly for client-side cleanup).
    """
    return {"message": "Successfully logged out"}

@router.get("/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    """
    Get current user information.
    """
    return {"username": current_user}

@router.get("/verify")
async def verify_token(current_user: str = Depends(get_current_user)):
    """
    Verify if the current token is valid.
    """
    return {"valid": True, "username": current_user}
