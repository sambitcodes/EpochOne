from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HealthConnectRecord(BaseModel):
    """Base record for Health Connect data."""
    start_time: datetime
    end_time: datetime
    metadata: Optional[dict] = None

class StepsRecord(HealthConnectRecord):
    count: int

class ActivityRecord(HealthConnectRecord):
    activity_type: str
    duration_minutes: float
    calories_burned: Optional[float] = None
    distance_meters: Optional[float] = None

class NutritionRecord(BaseModel):
    date: datetime
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    meal_type: Optional[str] = "unknown"
    name: Optional[str] = "Health Connect Import"

class BodyMetricRecord(BaseModel):
    date: datetime
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    body_fat_percent: Optional[float] = None

class HealthConnectSyncRequest(BaseModel):
    """Payload pushed from client."""
    steps: List[StepsRecord] = []
    activities: List[ActivityRecord] = []
    nutrition: List[NutritionRecord] = []
    body_metrics: List[BodyMetricRecord] = []
