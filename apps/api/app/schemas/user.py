"""
User request/response schemas.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Create user from Auth0 token or manual registration."""
    auth0_sub: Optional[str] = None
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

class UserRegister(BaseModel):
    """Manual user registration."""
    email: EmailStr
    username: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    """Manual user login."""
    username: str
    password: str

class UserUpdate(BaseModel):
    """Update user profile and settings."""
    name: Optional[str] = None
    units: Optional[str] = None
    calorie_target: Optional[int] = None
    protein_target: Optional[int] = None
    carb_target: Optional[int] = None
    fat_target: Optional[int] = None
    preferred_ai_model: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    target_weight: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    waist: Optional[int] = None
    neck: Optional[int] = None
    chest: Optional[int] = None
    thigh: Optional[int] = None
    hip: Optional[int] = None
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    lean_body_mass: Optional[float] = None
    maintenance_calories: Optional[int] = None
    step_goal: Optional[int] = None
    motive: Optional[str] = None
    lifestyle_type: Optional[str] = None
    workout_days_per_week: Optional[int] = None
    onboarding_complete: Optional[bool] = None
    picture: Optional[str] = None

class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    name: Optional[str]
    picture: Optional[str]
    units: str
    calorie_target: int
    protein_target: int
    xp: int
    level: int
    streak_workout: int
    weight: Optional[int] = None
    height: Optional[int] = None
    target_weight: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    waist: Optional[int] = None
    neck: Optional[int] = None
    chest: Optional[int] = None
    thigh: Optional[int] = None
    hip: Optional[int] = None
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    lean_body_mass: Optional[float] = None
    maintenance_calories: Optional[int] = None
    step_goal: int = 10000
    motive: Optional[str] = None
    lifestyle_type: Optional[str] = None
    workout_days_per_week: Optional[int] = None
    onboarding_complete: bool = False
    created_at: datetime

    class Config:
        from_attributes = True