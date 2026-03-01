"""
Authentication module for GynOrg
"""
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .config import settings

# Make HTTPBearer auto_error=False so we can manually check for a query token as a fallback
security = HTTPBearer(auto_error=False)

# Hardcoded fallback user credentials (as specified in requirements)
# These will be used if not overridden in .env or config
HARDCODED_USERNAME = "MGanser"
# bcrypt hash of "M4rvelf4n" with rounds=12
HARDCODED_PASSWORD_HASH = "$2b$12$8CDp40px7qcGwf/oB5IMFuhXA41WWuJhv8zC.OaZS2KLQgAJlNJ/e"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user with credentials from settings."""
    # Fallback to hardcoded username if not set in settings
    admin_username = getattr(settings, "ADMIN_USERNAME", HARDCODED_USERNAME)
    if username != admin_username:
        return False
    
    # Check for plain text password in settings (from .env)
    if hasattr(settings, "ADMIN_PASSWORD") and settings.ADMIN_PASSWORD is not None:
        return password == settings.ADMIN_PASSWORD
        
    admin_password_hash = getattr(settings, "ADMIN_PASSWORD_HASH", HARDCODED_PASSWORD_HASH)
    return verify_password(password, admin_password_hash)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check for token in query parameters first (for <img> tags, downloads, etc.)
    token = request.query_params.get("token")
    
    # If not in query, check Authorization header
    if not token:
        if credentials:
            token = credentials.credentials
        else:
            raise credentials_exception

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    admin_username = getattr(settings, "ADMIN_USERNAME", HARDCODED_USERNAME)
    if token_data.username != admin_username:
        raise credentials_exception
    
    return token_data.username

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[str]:
    """Get current user but allow None if no credentials provided."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        admin_username = getattr(settings, "ADMIN_USERNAME", HARDCODED_USERNAME)
        if username != admin_username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
