"""
Nutrition request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MealCreate(BaseModel):
    """Create meal entry."""
    name: str
    meal_type: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str] = None

class MealResponse(BaseModel):
    """Meal response."""
    id: str
    name: str
    date: datetime
    meal_type: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    ai_estimated: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MacroResponse(BaseModel):
    """Macro reference response."""
    id: str
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size: str

    class Config:
        from_attributes = True