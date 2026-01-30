"""
User profile and settings routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.metrics import BodyMetric
from app.models.activity import Activity
from app.models.wellness import WellnessLog
from app.schemas.user import UserResponse, UserUpdate
import logging
import csv
import io
import zipfile

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/export")
def export_user_data(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Export all user data as a ZIP of CSV files."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # In-memory ZIP buffer
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        
        # 1. Profile CSV
        profile_io = io.StringIO()
        writer = csv.writer(profile_io)
        writer.writerow(["Name", "Email", "Age", "Gender", "Weight", "Height", "Goal", "Lifestyle"])
        writer.writerow([
            user.name, user.email, user.age, user.gender, 
            user.weight, user.height, user.motive, user.lifestyle_type
        ])
        zip_file.writestr("profile.csv", profile_io.getvalue())

        # 2. Workouts CSV
        workouts = db.query(Workout).filter(Workout.user_id == user_id).all()
        workout_io = io.StringIO()
        writer = csv.writer(workout_io)
        writer.writerow(["Date", "Duration (min)", "Session Calories", "Exercise Name", "Sets", "Reps", "Weight", "Notes"])
        
        for w in workouts:
            # If workout has specific exercises, list them
            if w.exercises:
                for ex in w.exercises:
                    writer.writerow([
                        w.date, w.duration_minutes, w.calories_burned, 
                        ex.name, ex.sets, ex.reps, ex.weight, w.notes
                    ])
            else:
                # Just a session log without specific exercises (e.g. cardio or quick log)
                writer.writerow([
                    w.date, w.duration_minutes, w.calories_burned,
                    "General Session", "", "", "", w.notes
                ])
        zip_file.writestr("workouts.csv", workout_io.getvalue())

        # 3. Nutrition CSV
        meals = db.query(Meal).filter(Meal.user_id == user_id).all()
        meal_io = io.StringIO()
        writer = csv.writer(meal_io)
        writer.writerow(["Date", "Meal Type", "Name", "Calories", "Protein (g)", "Carbs (g)", "Fat (g)"])
        for m in meals:
            # Correct field names: protein_g, carbs_g, fat_g
            writer.writerow([m.date, m.meal_type, m.name, m.calories, m.protein_g, m.carbs_g, m.fat_g])
        zip_file.writestr("nutrition.csv", meal_io.getvalue())

        # 4. Body Metrics CSV (Key-Value Model)
        metrics = db.query(BodyMetric).filter(BodyMetric.user_id == user_id).all()
        metric_io = io.StringIO()
        writer = csv.writer(metric_io)
        writer.writerow(["Date", "Metric Type", "Value", "Unit", "Notes"])
        for m in metrics:
            writer.writerow([m.date, m.metric_type, m.value, m.unit, m.notes])
        zip_file.writestr("metrics.csv", metric_io.getvalue())
        
        # 5. Wellness CSV (Key-Value Model)
        wellness = db.query(WellnessLog).filter(WellnessLog.user_id == user_id).all()
        well_io = io.StringIO()
        writer = csv.writer(well_io)
        writer.writerow(["Date", "Metric Type", "Primary Value", "Secondary Value", "Notes"])
        for w in wellness:
            writer.writerow([w.date, w.metric_type, w.value_primary, w.value_secondary, w.notes])
        zip_file.writestr("wellness.csv", well_io.getvalue())

        # 6. Activity CSV
        activities = db.query(Activity).filter(Activity.user_id == user_id).all()
        act_io = io.StringIO()
        writer = csv.writer(act_io)
        writer.writerow(["Date", "Steps", "Total Calories", "Distance (km)", "Active Minutes"])
        for a in activities:
            writer.writerow([a.date, a.total_steps, a.total_calories, a.distance_km, a.active_minutes])
        zip_file.writestr("activity.csv", act_io.getvalue())

    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=epochone_export_{user_id}.zip"}
    )

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    update: UserUpdate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Update fields
    if update.name is not None:
        user.name = update.name
    if update.units is not None:
        user.units = update.units
    if update.calorie_target is not None:
        user.calorie_target = update.calorie_target
    if update.protein_target is not None:
        user.protein_target = update.protein_target
    if update.carb_target is not None:
        user.carb_target = update.carb_target
    if update.fat_target is not None:
        user.fat_target = update.fat_target
    if update.preferred_ai_model is not None:
        user.preferred_ai_model = update.preferred_ai_model
    if update.weight is not None:
        user.weight = update.weight
    if update.height is not None:
        user.height = update.height
    if update.target_weight is not None:
        user.target_weight = update.target_weight
    if update.age is not None:
        user.age = update.age
    if update.gender is not None:
        user.gender = update.gender
    if update.waist is not None:
        user.waist = update.waist
    if update.neck is not None:
        user.neck = update.neck
    if update.chest is not None:
        user.chest = update.chest
    if update.thigh is not None:
        user.thigh = update.thigh
    if update.hip is not None:
        user.hip = update.hip
    if update.body_fat_pct is not None:
        user.body_fat_pct = update.body_fat_pct
    if update.bmi is not None:
        user.bmi = update.bmi
    if update.lean_body_mass is not None:
        user.lean_body_mass = update.lean_body_mass
    if update.maintenance_calories is not None:
        user.maintenance_calories = update.maintenance_calories
    if update.step_goal is not None:
        user.step_goal = update.step_goal
    if update.motive is not None:
        user.motive = update.motive
    if update.lifestyle_type is not None:
        user.lifestyle_type = update.lifestyle_type
    if update.workout_days_per_week is not None:
        user.workout_days_per_week = update.workout_days_per_week
    if update.onboarding_complete is not None:
        user.onboarding_complete = update.onboarding_complete
    if update.picture is not None:
        user.picture = update.picture

    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} profile updated")
    return user

@router.get("/gamification")
def get_gamification(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get gamification stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {
        "xp": user.xp,
        "level": user.level,
        "streak_workout": user.streak_workout,
        "streak_nutrition": user.streak_nutrition,
        "next_level_xp": (user.level * 1000)  # Simple calculation
    }

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a user account and all associated data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    db.delete(user)
    db.commit()
    logger.info(f"User {user_id} account deleted")
    return None