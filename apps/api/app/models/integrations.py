"""
Integration state and sync models.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class HealthConnectSync(Base):
    """Health Connect sync state."""
    __tablename__ = "health_connect_sync"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    last_sync = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="idle")  # idle, syncing, error
    
    # Toggle what metrics to sync
    sync_steps = Column(Boolean, default=True)
    sync_activities = Column(Boolean, default=True)
    sync_calories = Column(Boolean, default=True)
    sync_heart_rate = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_connect_sync")

    def __repr__(self):
        return f"<HealthConnectSync {self.user_id[:8]}>"

class AppleHealthSync(Base):
    """Apple Health integration via iOS companion app."""
    __tablename__ = "apple_health_sync"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    # Webhook secret for iOS app to authenticate
    webhook_secret = Column(String(255), nullable=True)  # TODO: Implement
    
    last_sync = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="idle")
    
    # Toggle what metrics to sync
    sync_steps = Column(Boolean, default=True)
    sync_workouts = Column(Boolean, default=True)
    sync_sleep = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="apple_health_sync")

    def __repr__(self):
        return f"<AppleHealthSync {self.user_id[:8]}>"

class FitbitSync(Base):
    """Fitbit integration via OAuth2."""
    __tablename__ = "fitbit_sync"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    # OAuth2 Tokens
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=True)  # Timestamp
    
    last_sync = Column(DateTime, nullable=True)
    last_step_count = Column(Integer, default=0)
    last_calories_burned = Column(Integer, default=0)
    sync_status = Column(String(50), default="idle")
    
    # Toggle what metrics to sync
    sync_steps = Column(Boolean, default=True)
    sync_activities = Column(Boolean, default=True)
    sync_calories = Column(Boolean, default=True)
    sync_sleep = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="fitbit_sync")

    def __repr__(self):
        return f"<FitbitSync {self.user_id[:8]}>"