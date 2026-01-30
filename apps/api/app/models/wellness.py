from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from app.db import Base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class WellnessLog(Base):
    __tablename__ = "wellness_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Enum-like string: hrv, rhr, vo2max, bp, resp_rate, spo2, glucose
    metric_type = Column(String, nullable=False)
    
    # Primary value (e.g. Systolic for BP, or the main value)
    value_primary = Column(Float, nullable=False)
    
    # Secondary value (e.g. Diastolic for BP, optional for others)
    value_secondary = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="wellness_logs")
