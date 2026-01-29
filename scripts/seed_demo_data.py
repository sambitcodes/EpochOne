"""
Seed database with demo data for testing.
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import (
    User, Workout, WorkoutExercise, Activity, Meal, BodyMetric
)

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

def seed():
    """Seed demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create demo user
    demo_user = User(
        auth0_sub="demo|123456",
        email="demo@example.com",
        name="Demo User",
        units="metric",
        calorie_target=2200,
        xp=250,
        level=3
    )
    db.add(demo_user)
    db.flush()

    # Add some workouts
    for i in range(5):
        date = datetime.utcnow() - timedelta(days=i)
        workout = Workout(
            user_id=demo_user.id,
            date=date,
            duration_minutes=45 + (i * 5),
            rpe=7
        )
        db.add(workout)
        db.flush()

        # Add exercises
        exercises = [
            {"name": "Bench Press", "sets": 3, "reps": 8, "weight": 80},
            {"name": "Squats", "sets": 3, "reps": 8, "weight": 100},
            {"name": "Deadlifts", "sets": 2, "reps": 5, "weight": 120},
        ]

        for j, ex in enumerate(exercises):
            db.add(WorkoutExercise(
                workout_id=workout.id,
                name=ex["name"],
                sets=ex["sets"],
                reps=ex["reps"],
                weight=ex["weight"],
                order=j
            ))

    # Add activities
    for i in range(3):
        date = datetime.utcnow() - timedelta(days=i)
        db.add(Activity(
            user_id=demo_user.id,
            activity_type="running",
            date=date,
            duration_minutes=30,
            distance_km=5,
            intensity="moderate",
            calories_burned=250,
            source="manual"
        ))

    # Add meals
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        db.add(Meal(
            user_id=demo_user.id,
            date=date,
            name=f"Demo Meal {i}",
            meal_type="lunch",
            calories=600,
            protein_g=40,
            carbs_g=60,
            fat_g=20
        ))

    # Add body metrics
    db.add(BodyMetric(
        user_id=demo_user.id,
        date=datetime.utcnow(),
        metric_type="weight",
        value=75,
        unit="kg"
    ))

    db.commit()
    print("✅ Demo data seeded successfully!")
    print(f"   User: demo@example.com")
    print(f"   Auth0 sub: demo|123456")

if __name__ == "__main__":
    seed()