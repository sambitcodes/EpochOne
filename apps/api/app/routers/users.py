"""
User profile and settings routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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