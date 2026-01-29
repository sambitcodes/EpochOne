"""
Authentication routes (Auth0 OAuth callback and Manual Login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserRegister, UserLogin
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings
from passlib.context import CryptContext
import logging
import hashlib
import base64

# Password hashing context - switched to pbkdf2_sha256 to avoid bcrypt compatibility issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/auth0-callback", response_model=dict)
def auth0_callback(
    auth0_sub: str,
    email: str,
    name: str = None,
    picture: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Auth0 callback.
    In production, verify the Auth0 token first.
    """
    # Check if user exists
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

    if not user:
        # Create new user
        user = User(
            auth0_sub=auth0_sub,
            email=email,
            name=name,
            picture=picture
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {email}")
    else:
        # Update picture/name if provided
        if name:
            user.name = name
        if picture:
            user.picture = picture
        db.commit()
        db.refresh(user)

    return {
        "user_id": user.id,
        "email": user.email,
        "message": "Authenticated"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

@router.post("/register", response_model=dict)
def register_user(registration: UserRegister, db: Session = Depends(get_db)):
    """Manual user registration."""
    # Check if email exists
    if db.query(User).filter(User.email == registration.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    if db.query(User).filter(User.username == registration.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    user = User(
        email=registration.email,
        username=registration.username,
        hashed_password=get_password_hash(registration.password),
        name=registration.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Manual user registered: {user.username}")
    return {"message": "User registered successfully", "user_id": user.id}

@router.post("/login", response_model=dict)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Manual user login."""
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create token
    expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user.id,
        "email": user.email,
        "exp": expires
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/dev-login", response_model=dict)
def dev_login(db: Session = Depends(get_db)):
    """
    Dev only: Login as demo user and get token.
    """
    # Find demo user
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        # Check if demo user exists with username
        user = db.query(User).filter(User.username == "demo").first()
        
    if not user:
        raise HTTPException(status_code=404, detail="Demo user not found. Did you seed the DB?")

    # Create token
    expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user.id,
        "email": user.email,
        "exp": expires
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }