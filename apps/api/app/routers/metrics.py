"""
Body metrics and measurements routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.metrics import BodyMetric
from app.schemas.metrics import BodyMetricCreate, BodyMetricResponse
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=dict)
def log_metric(
    metric: BodyMetricCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log body metric (weight, measurement, etc.)."""
    db_metric = BodyMetric(
        user_id=user_id,
        metric_type=metric.metric_type,
        value=metric.value,
        unit=metric.unit,
        notes=metric.notes,
        date=datetime.utcnow()
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    logger.info(f"Metric logged: {metric.metric_type}={metric.value}{metric.unit}")
    return {"id": db_metric.id, "metric": metric.metric_type}

@router.get("/latest", response_model=dict)
def get_latest_metrics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get latest value for each metric type."""
    metric_types = ["weight", "chest", "waist", "biceps", "thighs"]
    latest = {}

    for mtype in metric_types:
        metric = db.query(BodyMetric).filter(
            BodyMetric.user_id == user_id,
            BodyMetric.metric_type == mtype
        ).order_by(BodyMetric.date.desc()).first()

        if metric:
            latest[mtype] = {
                "value": metric.value,
                "unit": metric.unit,
                "date": metric.date
            }

    return latest

@router.get("/history", response_model=List[dict])
def get_metric_history(
    user_id: str,
    metric_type: str,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get metric history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(BodyMetric).filter(
        BodyMetric.user_id == user_id,
        BodyMetric.metric_type == metric_type,
        BodyMetric.date >= cutoff
    ).order_by(BodyMetric.date.asc()).all()

    return [
        {
            "date": m.date,
            "value": m.value,
            "unit": m.unit
        }
        for m in metrics
    ]