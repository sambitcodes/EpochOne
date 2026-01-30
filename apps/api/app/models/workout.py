"""
Workout, exercise, and template models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class Workout(Base):
    """Completed workout session."""
    __tablename__ = "workouts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=False)  # Session duration
    calories_burned = Column(Integer, nullable=True)     # Estimated calories burned
    notes = Column(Text, nullable=True)
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion (1-10)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workout {self.id[:8]} ({self.date.date()})>"

class WorkoutExercise(Base):
    """Individual exercise within a workout."""
    __tablename__ = "workout_exercises"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String(36), ForeignKey("workouts.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # kg or lbs
    distance_km = Column(Float, nullable=True) # For cardio
    duration_seconds = Column(Integer, nullable=True) # For cardio
    rest_seconds = Column(Integer, nullable=True)
    failure = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")

    def __repr__(self):
        return f"<Exercise {self.name}>"

class WorkoutTemplate(Base):
    """Reusable workout template."""
    __tablename__ = "workout_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exercises_json = Column(Text, nullable=False)  # JSON serialized list of exercises
    last_used = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template {self.name}>"