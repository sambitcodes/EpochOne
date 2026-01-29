"""
Activity request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityCreate(BaseModel):
    """Create activity."""
    activity_type: str
    duration_minutes: int
    distance_km: Optional[float] = None
    intensity: Optional[str] = None
    calories_burned: Optional[float] = None
    notes: Optional[str] = None

class ActivityResponse(BaseModel):
    """Activity response."""
    id: str
    activity_type: str
    date: datetime
    duration_minutes: int
    distance_km: Optional[float]
    intensity: Optional[str]
    calories_burned: Optional[float]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True