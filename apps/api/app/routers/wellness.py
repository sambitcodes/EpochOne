from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.wellness import WellnessLog
from app.schemas.wellness import WellnessLogCreate, WellnessLogResponse
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/logs", response_model=WellnessLogResponse)
def create_wellness_log(
    log: WellnessLogCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new wellness log."""
    db_log = WellnessLog(
        user_id=user_id,
        date=log.date or datetime.utcnow(),
        metric_type=log.metric_type,
        value_primary=log.value_primary,
        value_secondary=log.value_secondary,
        notes=log.notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/logs", response_model=List[WellnessLogResponse])
def get_wellness_logs(
    user_id: str,
    metric_type: Optional[str] = None,
    days: int = 30,
    date_str: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get wellness history."""
    query = db.query(WellnessLog).filter(WellnessLog.user_id == user_id)
    
    if metric_type:
        query = query.filter(WellnessLog.metric_type == metric_type)
        
    if date_str:
        # Specific day filter
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            query = query.filter(WellnessLog.date >= start_of_day, WellnessLog.date <= end_of_day)
        except ValueError:
            pass # Ignore invalid date
    else:
        # History window
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(WellnessLog.date >= start_date)
    
    return query.order_by(WellnessLog.date.desc()).all()

@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wellness_log(
    log_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a wellness log."""
    log = db.query(WellnessLog).filter(
        WellnessLog.id == log_id,
        WellnessLog.user_id == user_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
        
    db.delete(log)
    db.commit()
    return None

@router.get("/analysis")
def get_wellness_analysis(
    user_id: str,
    metric_type: str,
    db: Session = Depends(get_db)
):
    """Get AI analysis for a specific metric."""
    # Fetch recent data
    logs = db.query(WellnessLog).filter(
        WellnessLog.user_id == user_id,
        WellnessLog.metric_type == metric_type
    ).order_by(WellnessLog.date.desc()).limit(10).all()
    
    if not logs:
        return {"tip": "Log some data to get AI insights!"}
        
    # Simple rule-based or AI call
    # For speed/simplicity in this iteration, using rule-based/mock AI or Groq call if key exists
    import os
    from app.integrations.groq_client import GroqCoach
    
    key = os.getenv("GROQ_API_KEY")
    if key and len(logs) >= 3:
        try:
            coach = GroqCoach(api_key=key)
            data_str = "\n".join([f"{l.date.strftime('%Y-%m-%d')}: {l.value_primary}" + (f"/{l.value_secondary}" if l.value_secondary else "") for l in logs])
            prompt = f"Analyze these {metric_type} readings and give 1 short health tip/warning (max 20 words): \n{data_str}"
            response = coach.chat(prompt, user_context={})
            return {"tip": response.get("text", "No insight available.")}
        except:
            pass
            
    return {"tip": "Keep tracking to see trends!"}
