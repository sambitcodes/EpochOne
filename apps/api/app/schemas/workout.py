"""
Workout request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class WorkoutExerciseCreate(BaseModel):
    """Create exercise within workout."""
    name: str
    sets: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    order: int = 0

class WorkoutCreate(BaseModel):
    """Create workout session."""
    duration_minutes: int
    rpe: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseCreate]

class WorkoutResponse(BaseModel):
    """Workout response."""
    id: str
    date: datetime
    duration_minutes: int
    rpe: Optional[int]
    calories_burned: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkoutTemplateCreate(BaseModel):
    """Create or update workout template."""
    name: str
    description: Optional[str] = None
    exercises: List[WorkoutExerciseCreate]

class WorkoutTemplateResponse(BaseModel):
    """Workout template response."""
    id: str
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True