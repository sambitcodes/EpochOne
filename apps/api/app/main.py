"""
FastAPI main application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv
import os

from app.config import settings
from app.db import engine, Base, SessionLocal
from app.routers import auth, workouts, activities, nutrition, metrics, integrations, ai_coach, users, wellness
from app.models.user import User
from app.routers.auth import get_password_hash

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ============ Lifespan ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    logger.info("Starting up and running migrations...")
    
    # Run Alembic migrations programmatically
    try:
        from alembic.config import Config
        from alembic import command
        
        # Point to the alembic.ini in the root directory (apps/api)
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        # We might want to continue even if migration fails, or re-raise
        # For now, logging error but allowing app to start (tables might be created by create_all fallback)
    
    # Create tables if not exist (fallback for dev)
    Base.metadata.create_all(bind=engine)
    
    # SEED DEMO USER
    try:
        db = SessionLocal()
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            logger.info("Seeding demo user...")
            demo_user = User(
                email="demo@example.com",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                name="Demo User"
            )
            db.add(demo_user)
            db.commit()
            logger.info("Demo user seeded successfully.")
        db.close()
    except Exception as e:
        logger.error(f"Seeding failed: {e}")

    yield
    logger.info("Shutting down...")

# ============ App ============

app = FastAPI(
    title="AI Fitness Tracker API",
    description="Backend for AI-powered fitness tracking",
    version="0.1.0",
    lifespan=lifespan
)

# ============ Middleware ============

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# ============ Routes ============

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(ai_coach.router, prefix="/ai-coach", tags=["ai_coach"])
app.include_router(wellness.router, prefix="/wellness", tags=["wellness"])

# ============ Health Check ============

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "api"}

@app.get("/", tags=["root"])
def root():
    """Root endpoint."""
    return {
        "name": "AI Fitness Tracker API",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)