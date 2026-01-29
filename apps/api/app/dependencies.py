"""
FastAPI dependency injection utilities.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from app.db import SessionLocal
from jose import JWTError, jwt
from app.config import settings
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify JWT token and return current user.
    In production, verify against Auth0 JWKS.
    """
    token = credentials.credentials

    try:
        # TODO: In production, fetch JWKS from Auth0 and verify signature
        # For MVP, we accept the token and extract claims
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return {"sub": user_id, "email": email}

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

async def get_current_user_async(
    credentials: HTTPAuthCredentials = Depends(security)
) -> dict:
    """Async version of get_current_user."""
    return get_current_user(credentials)