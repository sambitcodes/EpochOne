"""
Nutrition and macro tracking models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class DailyNutrition(Base):
    """Daily nutrition summary."""
    __tablename__ = "daily_nutrition"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    calories = Column(Integer, default=0)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Meal(Base):
    """Individual meal entry."""
    __tablename__ = "meals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    
    notes = Column(Text, nullable=True)
    ai_estimated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="meals")

    def __repr__(self):
        return f"<Meal {self.name}>"

class Macros(Base):
    """Quick macro reference for common foods."""
    __tablename__ = "macros"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    serving_size = Column(String(100), default="100g")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Macros {self.name}>"