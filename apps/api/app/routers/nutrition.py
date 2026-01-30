"""
Nutrition and meal logging routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.nutrition import Meal, DailyNutrition
from app.schemas.nutrition import MealCreate, MealResponse
from datetime import datetime, timedelta
from typing import List
import logging
from app.integrations.groq_client import GroqCoach
from app.config import settings
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)
router = APIRouter()

class MealEstimateRequest(BaseModel):
    description: str

class MealEstimateResponse(BaseModel):
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float

@router.post("/meals", response_model=dict)
def log_meal(
    meal: MealCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a meal."""
    db_meal = Meal(
        user_id=user_id,
        name=meal.name,
        meal_type=meal.meal_type,
        calories=meal.calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        notes=meal.notes,
        date=meal.date or datetime.utcnow()
    )

    # Update Streak
    try:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Check last meal date
            last_meal = db.query(Meal).filter(
                Meal.user_id == user_id
            ).order_by(Meal.date.desc()).first()
            
            current_date = (meal.date or datetime.utcnow()).date()
            
            if not last_meal:
                user.streak_nutrition = 1
            else:
                last_date = last_meal.date.date()
                delta = (current_date - last_date).days
                
                if delta == 1:
                    user.streak_nutrition += 1
                elif delta > 1:
                    user.streak_nutrition = 1
                # If delta == 0, keep same streak
            
            # XP for logging meal
            user.xp += 10
    except Exception as e:
        logger.error(f"Streak update failed: {e}")

    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    logger.info(f"Meal logged: {meal.name} for user {user_id}")
    return {"id": db_meal.id, "name": meal.name}

@router.post("/estimate", response_model=MealEstimateResponse)
def estimate_meal_macros(request: MealEstimateRequest):
    """Estimate meal macros using AI."""
    try:
        coach = GroqCoach(settings.GROQ_API_KEY)
        # Specific prompt for macro estimation
        prompt = f"""
        Estimate the nutritional content for this meal description: "{request.description}"
        Return ONLY a JSON object with these keys: 
        name, calories, protein_g, carbs_g, fat_g.
        Values should be realistic for a single serving.
        """
        
        response = coach.chat(prompt, mode="nutrition")
        text = response.get("text", "")
        
        # Extract JSON from text
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])
        
        return MealEstimateResponse(
            name=data.get("name", "Estimated Meal"),
            calories=int(data.get("calories", 0)),
            protein_g=float(data.get("protein_g", 0)),
            carbs_g=float(data.get("carbs_g", 0)),
            fat_g=float(data.get("fat_g", 0))
        )
    except Exception as e:
        logger.error(f"Macro estimation error: {e}")
        # Return a fallback or raise error
        return MealEstimateResponse(
            name="Manual Entry Required",
            calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0
        )

@router.get("/today", response_model=dict)
def get_today_nutrition(
    user_id: str,
    date_str: str = None,
    db: Session = Depends(get_db)
):
    """Get nutrition summary for a specific date (default: today UTC)."""
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.utcnow().date()
    else:
        target_date = datetime.utcnow().date()

    # Filter for the specific day (00:00 to 23:59)
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date >= start_of_day,
        Meal.date <= end_of_day
    ).all()

    total_calories = sum(m.calories for m in meals)
    total_protein = sum(m.protein_g for m in meals)
    total_carbs = sum(m.carbs_g for m in meals)
    total_fat = sum(m.fat_g for m in meals)

    return {
        "calories": total_calories,
        "protein_g": total_protein,
        "carbs_g": total_carbs,
        "fat_g": total_fat,
        "meal_count": len(meals)
    }

@router.get("/meals", response_model=List[dict])
def get_meals(
    user_id: str,
    days: int = 1,
    db: Session = Depends(get_db)
):
    """Get meals for past N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date >= cutoff
    ).order_by(Meal.date.desc()).all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "meal_type": m.meal_type,
            "calories": m.calories,
            "protein_g": m.protein_g,
            "date": m.date
        }
        for m in meals
    ]
@router.delete('/meals/{meal_id}', status_code=204)
def delete_meal(
    meal_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    '''Delete a meal.'''
    meal = db.query(Meal).filter(
        Meal.id == meal_id,
        Meal.user_id == user_id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail='Meal not found')
        
    db.delete(meal)
    db.commit()
    return None

