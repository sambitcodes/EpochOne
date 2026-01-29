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
from app.db import engine, Base
from app.routers import auth, workouts, activities, nutrition, metrics, integrations, ai_coach, users

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ============ Lifespan ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    logger.info("Starting up...")
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
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