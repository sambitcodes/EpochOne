from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WellnessLogBase(BaseModel):
    metric_type: str
    value_primary: float
    value_secondary: Optional[float] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None

class WellnessLogCreate(WellnessLogBase):
    pass

class WellnessLogResponse(WellnessLogBase):
    id: str
    user_id: str
    
    class Config:
        from_attributes = True
