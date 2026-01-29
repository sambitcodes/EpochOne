"""
Activity and wearable data models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class Activity(Base):
    """Logged activity (cardio, sports, etc.)."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    activity_type = Column(String(100), nullable=False)  # walk, run, swim, cycle, etc.
    date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=True)
    intensity = Column(String(50), nullable=True)  # easy, moderate, hard
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="manual")  # manual or google_fit

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity {self.activity_type} ({self.date.date()})>"