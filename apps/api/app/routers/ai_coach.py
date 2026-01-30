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
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

from app.models.chat import ChatThread, ChatMessage
from typing import List, Optional

class CoachMessage(BaseModel):
    """User message to coach."""
    message: str
    mode: str = "general"  # general, plan, nutrition, recovery, motivation, explain_data
    model: str = "llama-3.3-70b-versatile"
    thread_id: Optional[str] = None

class CoachResponse(BaseModel):
    """Coach response."""
    message: str
    actions: dict = {}  # Structured actions (JSON)
    requires_review: bool = False
    thread_id: str

class ThreadListItem(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/threads", response_model=List[ThreadListItem])
def list_threads(user_id: str, db: Session = Depends(get_db)):
    """List chat threads for a user."""
    return db.query(ChatThread).filter(
        ChatThread.user_id == user_id
    ).order_by(ChatThread.updated_at.desc()).all()

@router.get("/threads/{thread_id}/messages")
def get_thread_messages(thread_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get messages for a specific thread."""
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == user_id
    ).first()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    return [
        {
            "role": m.role,
            "content": m.content,
            "actions": m.actions,
            "created_at": m.created_at
        } for m in thread.messages
    ]

@router.delete("/threads/{thread_id}")
def delete_thread(thread_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete a chat thread."""
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == user_id
    ).first()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    db.delete(thread)
    db.commit()
    return {"status": "deleted"}

@router.post("/chat", response_model=CoachResponse)
def chat_with_coach(
    request: CoachMessage,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Chat with AI coach."""
    try:
        # 1. Get or Create Thread
        thread_id = request.thread_id
        if not thread_id:
            # Create a new thread with a snippet of the first message as title
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            thread = ChatThread(user_id=user_id, title=title)
            db.add(thread)
            db.commit()
            db.refresh(thread)
            thread_id = thread.id
        else:
            thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
            if not thread:
                raise HTTPException(status_code=404, detail="Thread not found")

        # 2. Fetch user profile for context
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

        # 3. Save User Message
        user_msg = ChatMessage(thread_id=thread_id, role="user", content=request.message)
        db.add(user_msg)
        db.flush() # Ensure it's in DB for history retrieval if needed, or just prepare context

        # 4. Fetch history for the thread (excluding the message we just added)
        history_msgs = db.query(ChatMessage).filter(
            ChatMessage.thread_id == thread_id,
            ChatMessage.id != user_msg.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        history = [
            {"role": m.role, "content": m.content} for m in history_msgs
        ]
        
        # 5. Get Coach Response
        coach = GroqCoach(settings.GROQ_API_KEY, request.model)
        
        response = coach.chat(
            message=request.message,
            mode=request.mode,
            user_id=user_id,
            user_context=user_context,
            history=history
        )

        message_text = response.get("text", "")
        actions = response.get("actions", {})

        # 5. Save AI Message
        ai_msg = ChatMessage(
            thread_id=thread_id, 
            role="assistant", 
            content=message_text,
            actions=actions
        )
        db.add(ai_msg)
        
        # Update thread timestamp
        thread.updated_at = datetime.utcnow()
        db.commit()

        return CoachResponse(
            message=message_text,
            actions=actions,
            requires_review=bool(actions),
            thread_id=thread_id
        )

    except HTTPException:
        raise
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
