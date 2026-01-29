"""
Body metrics and progress photo models.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class BodyMetric(Base):
    """Weight, measurements, and body composition."""
    __tablename__ = "body_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(100), nullable=False)  # weight, chest, waist, biceps, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")  # kg, lbs, cm, in
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="metrics")

    def __repr__(self):
        return f"<Metric {self.metric_type}: {self.value}{self.unit}>"

class ProgressPhoto(Base):
    """Progress photos for visual tracking."""
    __tablename__ = "progress_photos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    angle = Column(String(50), nullable=False)  # front, back, side_left, side_right
    photo_url = Column(String(500), nullable=False)  # S3 path or CDN URL
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Photo {self.angle} ({self.date.date()})>"