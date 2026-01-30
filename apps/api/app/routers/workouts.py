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
        date=workout.date or datetime.utcnow()
    )

    # Update Streak
    try:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Check last workout date
            last_workout = db.query(Workout).filter(
                Workout.user_id == user_id
            ).order_by(Workout.date.desc()).first()
            
            current_date = (workout.date or datetime.utcnow()).date()
            
            if not last_workout:
                user.streak_workout = 1
            else:
                last_date = last_workout.date.date()
                delta = (current_date - last_date).days
                
                if delta == 1:
                    user.streak_workout += 1
                elif delta > 1:
                    user.streak_workout = 1
                # If delta == 0, keep same streak
            
            # Update XP (Simple Gamification) for logging
            user.xp += 50
    except Exception as e:
        logger.error(f"Streak update failed: {e}")

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
            distance_km=ex.distance_km,
            duration_seconds=ex.duration_seconds,
            rest_seconds=ex.rest_seconds,
            failure=ex.failure,
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

@router.get("/daily-analysis", response_model=dict)
def get_daily_workout_analysis(
    user_id: str,
    date_str: str, # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """Get AI analysis for a specific day's workouts."""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        next_day = target_date + timedelta(days=1)
        
        workouts = db.query(Workout).filter(
            Workout.user_id == user_id,
            Workout.date >= target_date,
            Workout.date < next_day
        ).all()
        
        if not workouts:
            return {"analysis": "No workouts found for this day."}
            
        total_uns = len(workouts)
        total_mins = sum(w.duration_minutes for w in workouts)
        total_cals = sum(w.calories_burned or 0 for w in workouts)
        avg_rpe = sum(w.rpe or 0 for w in workouts) / total_uns if total_uns else 0
        
        # Format for AI
        summary = f"Total Workouts: {total_uns}\nTotal Duration: {total_mins} mins\nTotal Calories: {total_cals}\nAvg Intensity (RPE): {avg_rpe:.1f}/10\n\nExercises performed:\n"
        
        for w in workouts:
            for ex in w.exercises:
                details = ""
                if ex.distance_km:
                    details = f"{ex.distance_km}km in {ex.duration_seconds//60}min"
                else:
                    details = f"{ex.sets} sets x {ex.reps or 'N/A'} reps ({ex.weight or 0} kg)"
                
                if ex.failure:
                    details += " [FAILURE]"
                    
                summary += f" - {ex.name}: {details}\n"
                
        # Call AI
        from app.integrations.groq_client import GroqCoach
        import os
        key = os.getenv("GROQ_API_KEY")
        
        if key:
            coach = GroqCoach(api_key=key)
            prompt = f"Analyze this full day of training and provide 3 bullet points on recovery, nutrition, and fatigue management based on the volume and intensity. Be specific to the muscles worked. \n\n{summary}"
            response = coach.chat(prompt, user_context={})
            return {"analysis": response.get("text", "Analysis unavailable.")}
            
        return {"analysis": "AI Service unavailable."}
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"analysis": "Error generating analysis."}

@router.get("/today", response_model=dict)
def get_today_workouts(
    user_id: str,
    date_str: str = None,
    db: Session = Depends(get_db)
):
    """Get today's workout summary."""
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.utcnow().date()
    else:
        target_date = datetime.utcnow().date()

    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= start_of_day,
        Workout.date <= end_of_day
    ).all()

    total_calories = sum(w.calories_burned or 0 for w in workouts)
    
    return {
        "count": len(workouts),
        "calories": total_calories
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
        {"id": t.id, "name": t.name, "description": t.description, "exercises_json": t.exercises_json}
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
