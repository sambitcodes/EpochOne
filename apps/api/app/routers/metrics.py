"""
Body metrics and measurements routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from app.db import get_db
from app.models.metrics import BodyMetric
from app.models.user import User
from app.models.nutrition import DailyNutrition
from app.models.activity import Activity
from app.models.workout import Workout
from app.models.integrations import FitbitSync
from app.schemas.metrics import BodyMetricCreate, BodyMetricResponse
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/daily-summary", response_model=dict)
def get_daily_summary(
    user_id: str,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get consolidated daily calorie and burn summary."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.utcnow().date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    # 1. Get User Profile (Maintenance)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    maintenance = user.maintenance_calories or 2000 # Fallback
    
    # 2. Intake from DailyNutrition
    # Note: Using cast to Date might be slow on large tables without index on cast, but ok for MVP
    # Ideally DailyNutrition has a 'date' column that is DateTime. We filter by range.
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    daily_nut = db.query(DailyNutrition).filter(
        DailyNutrition.user_id == user_id,
        DailyNutrition.date >= start_of_day,
        DailyNutrition.date <= end_of_day
    ).first()
    
    intake = daily_nut.calories if daily_nut else 0
    
    # 3. Activity Burn
    activity_burn = db.query(func.sum(Activity.calories_burned)).filter(
        Activity.user_id == user_id,
        Activity.date >= start_of_day,
        Activity.date <= end_of_day
    ).scalar() or 0
    
    # 4. Workout Burn
    workout_burn = db.query(func.sum(Workout.calories_burned)).filter(
        Workout.user_id == user_id,
        Workout.date >= start_of_day,
        Workout.date <= end_of_day
    ).scalar() or 0
    
    # 5. Fitbit Logic (For reference: user might want to see it, but we use the formula requested)
    fitbit_burn = 0
    fitbit_sync = db.query(FitbitSync).filter(FitbitSync.user_id == user_id).first()
    if fitbit_sync and fitbit_sync.last_sync and fitbit_sync.last_sync.date() == target_date:
        fitbit_burn = fitbit_sync.last_calories_burned or 0
        
    # If Fitbit is reliable, maybe override activity_burn? 
    # User said: "maintenance + activities + workout". 
    # We will return explicit values.
    
    total_burn = maintenance + float(activity_burn) + float(workout_burn)
    net_calories = total_burn - float(intake)
    
    # If positive: Deficit (Burned > Intake) -> Wait, usually Net can be defined either way.
    # User said: "net deficit or net surplus".
    # Surplus = Intake - Burn. Deficit = Burn - Intake.
    # Let's return balance = Intake - TotalBurn. 
    # If -500, it's a 500 deficit. If +500, it's a 500 surplus.
    balance = float(intake) - total_burn
    
    return {
        "date": str(target_date),
        "maintenance_calories": maintenance,
        "bmr": user.maintenance_calories, # Using maintenance as proxy for BMR/TDEE base
        "calories_intake": intake,
        "calories_burned_activity": float(activity_burn),
        "calories_burned_workout": float(workout_burn),
        "calories_burned_fitbit": fitbit_burn,
        "total_expenditure": total_burn,
        "net_balance": balance, # Negative = Deficit
        "status": "Surplus" if balance > 0 else "Deficit"
    }

@router.post("/", response_model=dict)
def log_metric(
    metric: BodyMetricCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log body metric (weight, measurement, etc.)."""
    db_metric = BodyMetric(
        user_id=user_id,
        metric_type=metric.metric_type,
        value=metric.value,
        unit=metric.unit,
        notes=metric.notes,
        date=datetime.utcnow()
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    logger.info(f"Metric logged: {metric.metric_type}={metric.value}{metric.unit}")
    return {"id": db_metric.id, "metric": metric.metric_type}

@router.get("/latest", response_model=dict)
def get_latest_metrics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get latest value for each metric type."""
    metric_types = ["weight", "chest", "waist", "biceps", "thighs"]
    latest = {}

    for mtype in metric_types:
        metric = db.query(BodyMetric).filter(
            BodyMetric.user_id == user_id,
            BodyMetric.metric_type == mtype
        ).order_by(BodyMetric.date.desc()).first()

        if metric:
            latest[mtype] = {
                "value": metric.value,
                "unit": metric.unit,
                "date": metric.date
            }

    return latest

@router.get("/history", response_model=List[dict])
def get_metric_history(
    user_id: str,
    metric_type: str,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get metric history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(BodyMetric).filter(
        BodyMetric.user_id == user_id,
        BodyMetric.metric_type == metric_type,
        BodyMetric.date >= cutoff
    ).order_by(BodyMetric.date.asc()).all()

    return [
        {
            "date": m.date,
            "value": m.value,
            "unit": m.unit
        }
        for m in metrics
    ]