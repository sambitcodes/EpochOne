"""
Background job worker for sync, XP processing, and daily quests.
"""
import logging
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Setup logging first
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.api.app.models import User
from jobs import daily_quest_gen, xp_processor

# Database
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

def job_daily_quest_gen():
    """Generate daily quests for active users."""
    db = SessionLocal()
    try:
        daily_quest_gen.generate_daily_quests(db)
    finally:
        db.close()

def job_xp_processor():
    """Process XP and level calculations."""
    db = SessionLocal()
    try:
        xp_processor.process_xp(db)
    finally:
        db.close()

def main():
    """Start background scheduler."""
    scheduler = BackgroundScheduler()

    # Daily quest generation at 6 AM
    scheduler.add_job(
        job_daily_quest_gen,
        CronTrigger(hour=6, minute=0),
        id="daily_quest_gen"
    )

    # XP processing every hour
    scheduler.add_job(
        job_xp_processor,
        CronTrigger(minute=0),
        id="xp_processor"
    )

    scheduler.start()
    logger.info("Worker started")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Worker stopped")

if __name__ == "__main__":
    main()