"""
User model with Auth0 integration.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class User(Base):
    """User account with Auth0 integration."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auth0_sub = Column(String(255), unique=True, nullable=True, index=True)  # sub claim - nullable for manual users
    username = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(Text, nullable=True)

    # Physical Profile
    weight = Column(Integer, nullable=True)  # in units (kg or lbs)
    height = Column(Integer, nullable=True)  # in cm
    target_weight = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other
    
    # Measurements (in cm)
    waist = Column(Integer, nullable=True)
    neck = Column(Integer, nullable=True)
    chest = Column(Integer, nullable=True)
    thigh = Column(Integer, nullable=True)
    hip = Column(Integer, nullable=True)  # Needed for Navy Seal female formula
    
    # Calculated Stats
    bmi = Column(Float, nullable=True)
    body_fat_pct = Column(Float, nullable=True)
    lean_body_mass = Column(Integer, nullable=True)
    maintenance_calories = Column(Integer, nullable=True)
    step_goal = Column(Integer, default=10000)
    
    motive = Column(String(255), nullable=True)  # weight_loss, muscle_gain, endurance, health
    lifestyle_type = Column(String(255), nullable=True)  # sedentary, active, very_active
    workout_days_per_week = Column(Integer, nullable=True)
    onboarding_complete = Column(Boolean, default=False)

    # Settings
    units = Column(String(50), default="metric")  # metric, imperial
    calorie_target = Column(Integer, default=2200)
    protein_target = Column(Integer, default=150)  # grams
    carb_target = Column(Integer, default=250)
    fat_target = Column(Integer, default=73)
    preferred_ai_model = Column(String(100), default="llama-3.3-70b-versatile")

    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_workout = Column(Integer, default=0)
    streak_nutrition = Column(Integer, default=0)

    # Privacy & integrations
    health_connect_enabled = Column(Boolean, default=False)
    apple_health_enabled = Column(Boolean, default=False)
    share_profile = Column(Boolean, default=False)
    settings_json = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("BodyMetric", back_populates="user", cascade="all, delete-orphan")
    # Integrations
    health_connect_sync = relationship("HealthConnectSync", back_populates="user", uselist=False, cascade="all, delete-orphan")
    apple_health_sync = relationship("AppleHealthSync", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fitbit_sync = relationship("FitbitSync", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.auth0_sub})>"