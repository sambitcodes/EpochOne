"""
Body metrics request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BodyMetricCreate(BaseModel):
    """Create body metric."""
    metric_type: str
    value: float
    unit: str = "kg"
    notes: Optional[str] = None

class BodyMetricResponse(BaseModel):
    """Body metric response."""
    id: str
    date: datetime
    metric_type: str
    value: float
    unit: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProgressPhotoCreate(BaseModel):
    """Create progress photo."""
    angle: str
    photo_url: str
    notes: Optional[str] = None

class ProgressPhotoResponse(BaseModel):
    """Progress photo response."""
    id: str
    date: datetime
    angle: str
    photo_url: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True