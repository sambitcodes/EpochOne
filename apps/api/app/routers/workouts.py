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
    db_workout = Workout(
        user_id=user_id,
        duration_minutes=workout.duration_minutes,
        rpe=workout.rpe,
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
            "rpe": w.rpe
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