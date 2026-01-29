"""
AI Coach routes via Groq.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models.user import User
from app.integrations.groq_client import GroqCoach
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CoachMessage(BaseModel):
    """User message to coach."""
    message: str
    mode: str = "general"  # general, plan, nutrition, recovery, motivation, explain_data
    model: str = "llama-3.3-70b-versatile"

class CoachResponse(BaseModel):
    """Coach response."""
    message: str
    actions: dict = {}  # Structured actions (JSON)
    requires_review: bool = False

@router.post("/chat", response_model=CoachResponse)
def chat_with_coach(
    request: CoachMessage,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Chat with AI coach."""
    try:
        # Fetch user profile for context
        user = db.query(User).filter(User.id == user_id).first()
        user_context = {}
        if user:
            user_context = {
                "name": user.name,
                "weight_kg": user.weight,
                "height_cm": user.height,
                "goal": user.motive,
                "lifestyle": user.lifestyle_type,
                "workout_days_p_week": user.workout_days_per_week,
                "xp": user.xp,
                "level": user.level
            }

        coach = GroqCoach(settings.GROQ_API_KEY, request.model)
        response = coach.chat(
            message=request.message,
            mode=request.mode,
            user_id=user_id,
            user_context=user_context
        )

        return CoachResponse(
            message=response.get("text", ""),
            actions=response.get("actions", {}),
            requires_review=bool(response.get("actions"))
        )

    except Exception as e:
        logger.error(f"Coach error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Coach service error"
        )

@router.get("/models")
def get_available_models():
    """Get available Groq models."""
    return {
        "models": [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
            {"id": "groq/compound", "name": "Compound"},
            {"id": "openai/gpt-oss-120b", "name": "OpenAI GPT OSS 120B"}
        ]
    }

@router.post("/action/{action_id}/approve")
def approve_coach_action(
    action_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Approve and apply a coach action."""
    # TODO: Parse action_id, apply to user data
    logger.info(f"Action {action_id} approved by user {user_id}")
    return {"status": "approved"}

@router.get("/tip")
def get_daily_tip(user_id: str, db: Session = Depends(get_db)):
    """Get a quick personalized AI tip."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        user_context = {}
        if user:
            user_context = {
                "name": user.name,
                "weight_kg": user.weight,
                "height_cm": user.height,
                "goal": user.motive,
                "lifestyle": user.lifestyle_type
            }
        
        coach = GroqCoach(settings.GROQ_API_KEY)
        prompt = "Give a 1-sentence personalized fitness tip based on my current profile. Keep it brief and motivational."
        
        response = coach.chat(prompt, mode="motivation", user_context=user_context)
        return {"tip": response.get("text", "Keep pushing towards your goals!")}
    except Exception as e:
        logger.error(f"Tip error: {e}")
        return {"tip": "Stay hydrated and keep consistent!"}