import logging
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.nutrition import Meal, DailyNutrition
from app.models.metrics import BodyMetric
from app.models.integrations import HealthConnectSync
from app.schemas.integrations_health_connect import HealthConnectSyncRequest
from datetime import datetime

logger = logging.getLogger(__name__)

def process_health_connect_data(
    user_id: str,
    data: HealthConnectSyncRequest,
    db: Session
):
    """
    Process incoming Health Connect data and store it in the database.
    """
    try:
        # Update/Create Sync Record
        sync_record = db.query(HealthConnectSync).filter(
            HealthConnectSync.user_id == user_id
        ).first()

        if not sync_record:
            sync_record = HealthConnectSync(user_id=user_id)
            db.add(sync_record)
        
        sync_record.last_sync = datetime.utcnow()
        sync_record.sync_status = "syncing"
        db.commit()

        # 1. Process Activities
        count_activities = 0
        if sync_record.sync_activities:
            for act in data.activities:
                # Basic deduplication by checking date/user/type could be added here
                # For now, we append
                db_activity = Activity(
                    user_id=user_id,
                    activity_type=act.activity_type,
                    date=act.start_time,
                    duration_minutes=act.duration_minutes,
                    calories_burned=act.calories_burned,
                    distance_km=(act.distance_meters / 1000.0) if act.distance_meters else None,
                    source="health_connect"
                )
                db.add(db_activity)
                count_activities += 1
        
        # 2. Process Nutrition
        count_meals = 0
        if sync_record.sync_calories:
            for nut in data.nutrition:
                db_meal = Meal(
                    user_id=user_id,
                    name=nut.name or "Health Connect Import",
                    meal_type=nut.meal_type or "unknown",
                    date=nut.date,
                    calories=int(nut.calories or 0),
                    protein_g=nut.protein or 0,
                    carbs_g=nut.carbs or 0,
                    fat_g=nut.fat or 0,
                    notes="Imported from Health Connect"
                )
                db.add(db_meal)
                count_meals += 1
        
        # 3. Process Body Metrics
        count_metrics = 0
        for metric in data.body_metrics:
            if metric.weight_kg:
                db.add(BodyMetric(
                    user_id=user_id,
                    date=metric.date,
                    metric_type="weight",
                    value=metric.weight_kg,
                    unit="kg",
                    notes="Health Connect"
                ))
                count_metrics += 1
            # Add other metrics if needed

        sync_record.sync_status = "success"
        db.commit()
        
        logger.info(
            f"Health Connect Sync for {user_id}: "
            f"{count_activities} activities, {count_meals} meals, {count_metrics} metrics"
        )
        return {
            "status": "success",
            "activities": count_activities,
            "meals": count_meals,
            "metrics": count_metrics
        }

    except Exception as e:
        logger.error(f"Health Connect sync error for {user_id}: {e}")
        if sync_record:
            sync_record.sync_status = "error"
            db.commit()
        raise e
