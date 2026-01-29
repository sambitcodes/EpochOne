"""
Daily quest generation job.
"""
import logging
import random
from sqlalchemy.orm import Session
from apps.api.app.models import User
from datetime import datetime

logger = logging.getLogger(__name__)

QUESTS = [
    {"name": "Step Goal", "target": 10000, "xp_reward": 50},
    {"name": "Protein Goal", "target": 150, "xp_reward": 50},
    {"name": "Complete Workout", "target": 1, "xp_reward": 75},
    {"name": "Hydration Check", "target": 8, "xp_reward": 25},
    {"name": "Sleep 8 Hours", "target": 8, "xp_reward": 50},
]

def generate_daily_quests(db: Session):
    """Generate daily quests for all users."""
    users = db.query(User).all()

    for user in users:
        # TODO: Create daily quest records
        selected = random.sample(QUESTS, k=min(3, len(QUESTS)))
        logger.info(f"Generated {len(selected)} quests for user {user.id}")