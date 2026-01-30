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
    date: Optional[str] = None, # accepts date_str
    db: Session = Depends(get_db)
):
    """Get consolidated daily calorie and burn summary (IST aware)."""
    # 0. Import Models
    from app.models.nutrition import Meal
    
    # 1. Determine Target Date (IST)
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    else:
        target_date = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
        
    # 2. Get User Profile & Calculate BMR (Mifflin-St Jeor)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Defaults
    w = user.weight or 70.0
    h = user.height or 170.0
    a = user.age or 30
    g = (user.gender or 'male').lower()
    
    # Format: (10*W) + (6.25*H) - (5*A) + S
    # S: +5 for men, -161 for women
    s_val = 5 if g in ['male', 'm'] else -161
    bmr = (10 * w) + (6.25 * h) - (5 * a) + s_val
    bmr = int(bmr) # Keep it integer
        
    # 3. Calculate UTC Range for this IST Day
    start_ist = datetime.combine(target_date, datetime.min.time())
    end_ist = datetime.combine(target_date, datetime.max.time())
    
    start_utc = start_ist - timedelta(hours=5, minutes=30)
    end_utc = end_ist - timedelta(hours=5, minutes=30)
    
    # 4. Intake (From Meals)
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date >= start_utc,
        Meal.date <= end_utc
    ).all()
    
    intake = sum(m.calories for m in meals)
    
    # 5. Activity Burn (Manual Activities)
    manual_activity_burn = db.query(func.sum(Activity.calories_burned)).filter(
        Activity.user_id == user_id,
        Activity.date >= start_utc,
        Activity.date <= end_utc
    ).scalar() or 0
    
    # 6. Step Burn (Fitbit / AI Estimate)
    step_burn = 0
    from app.models.integrations import FitbitSync
    fitbit_sync = db.query(FitbitSync).filter(FitbitSync.user_id == user_id).first()
    
    if fitbit_sync and fitbit_sync.last_sync:
         # Check sync time in IST
         sync_ist = fitbit_sync.last_sync + timedelta(hours=5, minutes=30)
         if sync_ist.date() == target_date:
             # Formula: Steps * 0.045
             step_burn = fitbit_sync.last_step_count * 0.045
    
    # 7. Workout Burn
    workout_burn = db.query(func.sum(Workout.calories_burned)).filter(
        Workout.user_id == user_id,
        Workout.date >= start_utc,
        Workout.date <= end_utc
    ).scalar() or 0
    
    # 8. Totals
    # User Request: "Activity Burn should include steps". 
    total_activity_burn = float(manual_activity_burn) + float(step_burn)
    
    # Total Burn = BMR + Activity(Manual+Steps) + Workout
    total_expenditure = bmr + total_activity_burn + float(workout_burn)
    
    # Net Balance = Intake - Expenditure
    balance = float(intake) - total_expenditure
    
    return {
        "date": str(target_date),
        "maintenance_calories": bmr, # Using BMR logic as requested
        "bmr": bmr,
        "calories_intake": intake,
        "calories_burned_activity": total_activity_burn, # Includes Steps + Manual
        "calories_burned_workout": float(workout_burn),
        "calories_burned_step": step_burn,
        "total_expenditure": total_expenditure,
        "net_balance": balance,
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