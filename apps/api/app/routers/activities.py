"""
Activity logging routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/log", response_model=dict)
def log_activity(
    activity: ActivityCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a manual activity."""
    # Fetch user for context
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    
    cals = activity.calories_burned
    
    # AI Estimation if needed
    if (not cals or cals == 0) and user:
        try:
            from app.integrations.groq_client import GroqCoach
            import os
            
            key = os.getenv("GROQ_API_KEY")
            if key:
                coach = GroqCoach(api_key=key)
                context = {
                    "weight": user.weight,
                    "height": user.height,
                    "age": user.age,
                    "gender": user.gender
                }
                desc = f"{activity.activity_type} - {activity.intensity or 'moderate'}"
                cals = coach.estimate_calories(desc, activity.duration_minutes, context)
        except Exception as e:
            logger.error(f"AI estimation error: {e}")
            cals = 0  # Fallback
            
    db_activity = Activity(
        user_id=user_id,
        activity_type=activity.activity_type,
        duration_minutes=activity.duration_minutes,
        distance_km=activity.distance_km,
        intensity=activity.intensity,
        calories_burned=cals,
        notes=activity.notes,
        source="manual",
        date=datetime.utcnow()
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    logger.info(f"Activity logged: {activity.activity_type} for user {user_id} (Cals: {cals})")
    return {"id": db_activity.id, "type": activity.activity_type, "calories": cals}

@router.get("/today", response_model=dict)
def get_today_activity(
    user_id: str,
    date_str: str = None,
    db: Session = Depends(get_db)
):
    """Get today's activities summary (IST aware)."""
    # 1. Determine Target Date (IST)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    else:
        target_date = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()

    # 2. Calculate UTC Range for this IST Day
    # Start: TargetDay 00:00 IST -> -5:30 -> PreviousDay 18:30 UTC
    # End: TargetDay 23:59 IST -> -5:30 -> TargetDay 18:29 UTC
    start_ist = datetime.combine(target_date, datetime.min.time())
    end_ist = datetime.combine(target_date, datetime.max.time())
    
    start_utc = start_ist - timedelta(hours=5, minutes=30)
    end_utc = end_ist - timedelta(hours=5, minutes=30)

    # 3. Fetch Manual Activities
    activities = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.date >= start_utc,
        Activity.date <= end_utc
    ).all()

    total_distance = sum(a.distance_km or 0 for a in activities)
    manual_calories = sum(a.calories_burned or 0 for a in activities)
    total_duration = sum(a.duration_minutes or 0 for a in activities)

    today_stats = {
        "total_activities": len(activities),
        "total_duration_minutes": total_duration,
        "total_distance_km": total_distance,
        "manual_calories": manual_calories,
        "step_calories": 0,
        "total_calories": manual_calories, # Will update with steps
        "total_steps": 0
    }

    # 4. Merge Fitbit Steps / AI Step Calc
    from app.models.integrations import FitbitSync
    fitbit = db.query(FitbitSync).filter(FitbitSync.user_id == user_id).first()
    
    if fitbit and fitbit.last_sync:
        # Check if sync was today (Convert UTC sync time to IST date)
        sync_ist = fitbit.last_sync + timedelta(hours=5, minutes=30)
        
        if sync_ist.date() == target_date:
            steps = fitbit.last_step_count
            today_stats["total_steps"] = steps
            
            # AI/Formula Calculation: 0.045 kcal/step (Standard/Active)
            # This is "individually calculated" as requested, separate from BMR.
            step_cals = steps * 0.045
            today_stats["step_calories"] = step_cals
            today_stats["total_calories"] += step_cals
            
    return today_stats

@router.get("/history", response_model=List[dict])
def get_activity_history(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get activity history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    activities = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.date >= cutoff
    ).order_by(Activity.date.desc()).all()

    return [
        {
            "id": a.id,
            "type": a.activity_type,
            "date": a.date,
            "duration_minutes": a.duration_minutes,
            "distance_km": a.distance_km,
            "calories": a.calories_burned
        }
        for a in activities
    ]
@router.delete('/{activity_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    '''Delete an activity.'''
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == user_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail='Activity not found')
        
    db.delete(activity)
    db.commit()
    return None

