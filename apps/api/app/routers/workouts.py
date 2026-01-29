"""
Workout logging and template routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.workout import Workout, WorkoutExercise, WorkoutTemplate
from app.schemas.workout import (
    WorkoutCreate, WorkoutResponse, WorkoutTemplateCreate, WorkoutTemplateResponse
)
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/log", response_model=dict)
def log_workout(
    workout: WorkoutCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a new workout."""
    # AI Calorie Estimation
    cals = workout.calories_burned
    
    if not cals or cals == 0:
        try:
            from app.models.user import User
            from app.integrations.groq_client import GroqCoach
            import os
            
            user = db.query(User).filter(User.id == user_id).first()
            key = os.getenv("GROQ_API_KEY")
            
            if user and key:
                coach = GroqCoach(api_key=key)
                context = {
                    "weight": user.weight,
                    "height": user.height,
                    "age": user.age,
                    "gender": user.gender
                }
                
                # Construct description from exercises
                ex_list = ", ".join([f"{e.sets}x {e.name}" for e in workout.exercises])
                desc = f"Strength Workout (RPE {workout.rpe}): {ex_list}"
                
                cals = coach.estimate_calories(desc, workout.duration_minutes, context)
        except Exception as e:
            logger.error(f"Workout AI Calorie Est failed: {e}")

    db_workout = Workout(
        user_id=user_id,
        duration_minutes=workout.duration_minutes,
        rpe=workout.rpe,
        calories_burned=cals,
        notes=workout.notes,
        date=datetime.utcnow()
    )
    db.add(db_workout)
    db.flush()

    # Add exercises
    for i, ex in enumerate(workout.exercises):
        db_exercise = WorkoutExercise(
            workout_id=db_workout.id,
            name=ex.name,
            sets=ex.sets,
            reps=ex.reps,
            weight=ex.weight,
            rest_seconds=ex.rest_seconds,
            notes=ex.notes,
            order=i
        )
        db.add(db_exercise)

    db.commit()
    db.refresh(db_workout)
    logger.info(f"Workout logged for user {user_id}")

    return {
        "id": db_workout.id,
        "date": db_workout.date,
        "exercises_count": len(workout.exercises)
    }

@router.get("/history", response_model=List[dict])
def get_workout_history(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get workout history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= cutoff
    ).order_by(Workout.date.desc()).all()

    return [
        {
            "id": w.id,
            "date": w.date,
            "duration_minutes": w.duration_minutes,
            "exercise_count": len(w.exercises),
            "rpe": w.rpe,
            "calories_burned": w.calories_burned
        }
        for w in workouts
    ]

@router.post("/templates", response_model=dict)
def create_template(
    template: WorkoutTemplateCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create workout template."""
    import json
    db_template = WorkoutTemplate(
        user_id=user_id,
        name=template.name,
        description=template.description,
        exercises_json=json.dumps(
            [ex.dict() for ex in template.exercises]
        )
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return {"id": db_template.id, "name": db_template.name}

@router.get("/templates", response_model=List[dict])
def get_templates(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's workout templates."""
    templates = db.query(WorkoutTemplate).filter(
        WorkoutTemplate.user_id == user_id
    ).all()
    return [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in templates
    ]
@router.delete('/{workout_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    '''Delete a workout.'''
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == user_id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail='Workout not found')
        
    db.delete(workout)
    db.commit()
    return None

