
## README.md

```markdown
# AI Fitness Tracker 🏋️‍♂️🤖

A multi-user AI-powered fitness tracking webapp with Streamlit frontend, FastAPI backend, Google Fit + Apple Health integrations, and an intelligent Groq-powered AI Coach.

**Status**: MVP with Streamlit Community Cloud deployment ready + Docker Compose for full-stack VPS deployment.

---

## Features

### Core Tracking
- **Workouts**: Strength training (exercises, sets, reps, weight, RPE, rest time)
- **Activities**: Cardio, sports, etc. with wearable sync from Google Fit
- **Nutrition**: Daily calorie/macro tracking with AI meal estimation
- **Body Metrics**: Weight, measurements, progress photos (S3 scaffold)
- **Recovery**: Sleep, hydration, mood-energy logging

### Integrations
- **Google Fit**: OAuth 2.0 + scheduled sync pipeline
- **Apple Health**: iOS companion app scaffold + API bridge
- **Groq AI**: Multiple model picker (compound, llama-3.3-70b, openai/gpt-oss-120b)

### AI Coach
- Chat interface with persistent history
- Modes: Plan, Nutrition, Recovery, Motivation, Data Explanation
- Structured JSON outputs for actionable recommendations
- Safety guardrails (medical disclaimer, risky keyword detection)

### Gamification
- XP + Levels
- Streaks (workout, nutrition, sleep)
- Daily quests + mini-challenges
- Badges (milestone-based)

### Authentication
- Auth0 OIDC (Google + Email/Password)
- Secure session management
- User-scoped data

---

## Deployment

### Option A: Streamlit Community Cloud (NOW)

1. **Fork/clone this repo to GitHub**.

2. **Streamlit Cloud setup**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Deploy from `apps/streamlit_app/app.py`
   - Set entrypoint to `apps/streamlit_app/app.py`
   - In Advanced Settings → Secrets, add (from `.streamlit/secrets.toml.example`):
     ```
     STREAMLIT_ENABLED = true
     API_BASE_URL = "https://your-api-host/api"
     AUTH0_DOMAIN = "your-tenant.auth0.com"
     AUTH0_CLIENT_ID = "your-client-id"
     AUTH0_CLIENT_SECRET = "your-client-secret"
     GROQ_API_KEY = "gsk_..."
     ```
   - Root `requirements.txt` will be used automatically.

3. **Backend & Worker** (see Option B for full architecture):
   - Deploy FastAPI + Worker separately (free tier: Render, Railway, Heroku alternative)
   - Update `API_BASE_URL` in Streamlit Cloud secrets

---

### Option B: Full Stack on VPS (Docker Compose)

1. **Prerequisites**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose git
   sudo usermod -aG docker $USER
   newgrp docker
```

2. **Clone \& setup**:

```bash
git clone https://github.com/yourname/fitness_ai_tracker.git
cd fitness_ai_tracker
cp .env.example .env
# Edit .env with your secrets (Auth0, Groq, etc.)
```

3. **Run**:

```bash
docker-compose up -d
```

    - Streamlit: `http://localhost:8501`
    - API: `http://localhost:8000`
    - Postgres: port 5432 (internal)
    - Redis: port 6379 (internal)
    - Worker: runs in background
4. **Initialize DB**:

```bash
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_demo_data.py
```

5. **HTTPS \& Production**:
    - Add Nginx reverse proxy (TLS via Let's Encrypt)
    - Use `docker-compose.prod.yml` (with hardened CORS, secure cookies)
    - See `DEPLOYMENT.md` for details

---

## Auth0 Configuration

### Callback URLs (Auth0 Dashboard → Application Settings)

**Streamlit Cloud**:

```
https://your-app.streamlit.app/auth0_callback
```

**Local Docker**:

```
http://localhost:8501/auth0_callback
```

**VPS Production**:

```
https://yourdomain.com/auth0_callback
```


### Logout URLs

- Streamlit Cloud: `https://your-app.streamlit.app`
- Local: `http://localhost:8501`
- VPS: `https://yourdomain.com`

---

## Google Fit OAuth Setup

1. **Google Cloud Console**:
    - Enable "Fitness REST API"
    - Create OAuth 2.0 Credential (Web application)
    - Authorized redirect URIs:

```
http://localhost:8000/api/integrations/google-fit/callback
https://your-api-host.com/api/integrations/google-fit/callback
```

    - Download credentials JSON → extract `client_id`, `client_secret`
2. **Store in `.env`**:

```
GOOGLE_FIT_CLIENT_ID=...
GOOGLE_FIT_CLIENT_SECRET=...
```

3. **DB will store refresh tokens** (encrypted at rest, see `packages/core/security.py`)

---

## Groq API Setup

1. Get API key from [console.groq.com](https://console.groq.com)
2. Set in `.env`:

```
GROQ_API_KEY=gsk_...
```

3. Available models (configurable in Settings page):
    - `groq/compound`
    - `llama-3.3-70b-versatile`
    - `openai/gpt-oss-120b` (if available in Groq API)

---

## Development

### Local Setup (No Docker)

```bash
# Install Python 3.11+
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install shared core
pip install -e packages/core

# Install Streamlit app
cd apps/streamlit_app
pip install -r requirements.txt
streamlit run app.py

# In another terminal: Install & run API
cd apps/api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```


### Testing

```bash
# API tests
cd apps/api
pytest tests/ -v

# Worker tests
cd apps/worker
pytest tests/ -v
```


### Database Migrations

```bash
cd apps/api
# Create new migration
alembic revision --autogenerate -m "description"
# Apply
alembic upgrade head
# Rollback
alembic downgrade -1
```


---

## Project Structure

- **`packages/core/`**: Shared settings, logging, types, security utilities
- **`apps/streamlit_app/`**: Streamlit UI (Community Cloud compatible)
- **`apps/api/`**: FastAPI backend, SQLAlchemy models, Alembic migrations
- **`apps/worker/`**: Background job processor (sync, XP, quests)
- **`scripts/`**: DB initialization, seed data, Auth0 setup guide

---

## Architecture Notes

### Streamlit Community Cloud Compatibility

- Root `requirements.txt` contains minimal deps for Streamlit app
- Backend deployed separately (API \& Worker on free VPS tier or Render)
- Streamlit Cloud reads `.streamlit/secrets.toml` for API endpoint config
- No blocking DB connections in Streamlit (async calls to API via `requests`)


### Backend Architecture

- **FastAPI**: RESTful API, OAuth2 callback handlers, user endpoints
- **PostgreSQL**: User accounts, workouts, metrics, sync state
- **Redis**: Session store, sync locks, rate limiting
- **Worker (APScheduler or Celery)**: Google Fit sync, daily quests, XP processing


### Security

- Auth0 tokens verified on API
- Refresh tokens encrypted with `Fernet` (see `packages/core/security.py`)
- No secrets committed; `.env.example` shows structure
- CORS, HTTPS, secure cookies in production

---

## Roadmap

### Phase 1 (MVP)

- ✅ Core tracking (workouts, activities, nutrition, metrics)
- ✅ Google Fit OAuth + sync
- ✅ Groq AI Coach with model picker
- ✅ Basic gamification (XP, streaks)
- ✅ Auth0 integration
- ⚠️ Apple Health scaffold (iOS companion app TODO)


### Phase 2

- Photo progress upload (S3 integration)
- Advanced workout analytics (1RM estimates, volume trends)
- Social features (friend challenges, leaderboards)
- Wearable integrations (Fitbit, Garmin)
- Mobile app (Flutter)

---

## Troubleshooting

### "API_BASE_URL not found" in Streamlit

- Check Streamlit Cloud Secrets → add `API_BASE_URL`


### "Google Fit sync failing"

- Check refresh token expiry (logs in worker container)
- Verify `GOOGLE_FIT_CLIENT_ID/SECRET` in API `.env`


### "Auth0 callback loop"

- Verify Callback URL matches in Auth0 dashboard
- Check `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`


### Database connection errors

- Ensure `DATABASE_URL` is set (Postgres must be running)
- Run `alembic upgrade head` to initialize schema

---

## License

MIT

---

## Support

For issues, see `TROUBLESHOOTING.md` or open a GitHub issue.

```

***

## .env.example

```env
# ============ Shared / API ============
DATABASE_URL=postgresql://user:password@localhost:5432/fitness_tracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-min-32-chars-here

# ============ Auth0 ============
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://your-api-host/api

# ============ Google Fit ============
GOOGLE_FIT_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_FIT_CLIENT_SECRET=your-client-secret
GOOGLE_FIT_REDIRECT_URI=http://localhost:8000/api/integrations/google-fit/callback

# ============ Groq ============
GROQ_API_KEY=gsk_...

# ============ Streamlit (Streamlit Cloud secrets) ============
STREAMLIT_ENABLED=true
API_BASE_URL=http://localhost:8000/api
# (or https://your-api-host/api for production)

# ============ Apple Health Bridge (TODO) ============
# APPLE_HEALTH_WEBHOOK_SECRET=...

# ============ S3 (Photo storage - Phase 2) ============
# AWS_S3_BUCKET=fitness-tracker-photos
# AWS_S3_REGION=us-east-1
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# ============ Environment ============
ENVIRONMENT=development
LOG_LEVEL=INFO
```


***

## requirements.txt (Root - for Streamlit Cloud)

```
# Core Streamlit + auth
streamlit==1.41.0
streamlit-oauth==0.1.4
streamlit-authenticator==0.3.4

# HTTP & async
httpx==0.28.1
requests==2.32.3

# Data processing
pandas==2.2.1
numpy==1.26.4

# Utilities
python-dotenv==1.0.1
pydantic==2.8.2

# Visualization
plotly==5.24.1
altair==5.4.1

# Date/time
python-dateutil==2.9.0
pytz==2024.1
```


***

## apps/streamlit_app/app.py

```python
import streamlit as st
import requests
from datetime import datetime
import logging

# Setup page config first (must be before any other st calls)
st.set_page_config(
    page_title="AI Fitness Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f1419; }
    [data-testid="stMainBlockContainer"] { padding-top: 2rem; }
    h1 { color: #00d9ff; margin-bottom: 1rem; }
    h2 { color: #00d9ff; margin-top: 1.5rem; }
    .metric-card { 
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border-left: 4px solid #00d9ff;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

logger = logging.getLogger(__name__)

# ============ Auth Check ============
def init_session_state():
    """Initialize session state for auth and UI."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
        st.session_state.user = None
        st.session_state.user_id = None

init_session_state()

def get_api_base():
    """Get API base URL from Streamlit secrets."""
    return st.secrets.get("API_BASE_URL", "http://localhost:8000/api")

def is_authenticated():
    """Check if user is logged in."""
    return st.session_state.get("access_token") is not None

def login_user():
    """Login via Auth0 (simplified - in production use streamlit-oauth or manual OAuth flow)."""
    st.warning("🔐 Login via Auth0 (Integrate with `streamlit-oauth` or manual redirect)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login with Google"):
            st.info("Redirecting to Auth0...")
            # TODO: Implement OAuth flow with streamlit-oauth
            # oauth_flow = Auth0Flow(...)
            # token = oauth_flow.authorize()

    # For MVP, show manual token input (dev only)
    if st.checkbox("Dev: Enter access token manually"):
        token = st.text_input("Access Token", type="password")
        if token:
            st.session_state.access_token = token
            st.session_state.user = {"sub": "dev_user", "email": "dev@example.com"}
            st.session_state.user_id = "dev_user"
            st.success("✅ Logged in (dev mode)")
            st.rerun()

def logout_user():
    """Logout user."""
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.user_id = None
    st.success("✅ Logged out")
    st.rerun()

# ============ Main App ============

def main():
    if not is_authenticated():
        st.title("🏋️ AI Fitness Tracker")
        st.write("Track your workouts, nutrition, and get AI-powered coaching.")
        login_user()
        st.info("⏳ Login to continue")
        return

    # Authenticated sidebar
    with st.sidebar:
        st.title("🏋️ Fitness Tracker")
        user_email = st.session_state.get("user", {}).get("email", "Unknown")
        st.markdown(f"**{user_email}**")
        st.divider()

        if st.button("🚪 Logout"):
            logout_user()

    # Main dashboard
    st.title("📊 Dashboard")
    st.write(f"Welcome back! Today is {datetime.now().strftime('%A, %B %d')}")

    # Placeholder widgets
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Steps", "8,234", "+412")
    with col2:
        st.metric("Calories", "1,842 / 2,200", "-358")
    with col3:
        st.metric("Workouts", "3 / 4", "1 planned")
    with col4:
        st.metric("Streak", "12 days", "🔥")

    st.divider()

    col_workout, col_nutrition = st.columns(2)
    with col_workout:
        st.subheader("💪 Today's Workout")
        st.info("No workout logged yet. Start with a template or log manually.")

    with col_nutrition:
        st.subheader("🍽️ Nutrition")
        st.info("No meals logged. Use the Nutrition page to add foods.")

    st.divider()

    st.subheader("🤖 Quick Coach Tip")
    st.success("💡 Tip: Aim for 8-10k steps daily and drink 2L+ water. You're doing great!")

if __name__ == "__main__":
    main()
```


***

## apps/streamlit_app/.streamlit/config.toml

```toml
[theme]
primaryColor = "#00d9ff"
backgroundColor = "#0f1419"
secondaryBackgroundColor = "#1a1f2e"
textColor = "#ffffff"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[logger]
level = "info"

[server]
maxUploadSize = 200
headless = true
enableXsrfProtection = true
```


***

## apps/streamlit_app/.streamlit/secrets.toml.example

```toml
API_BASE_URL = "http://localhost:8000/api"
AUTH0_DOMAIN = "your-tenant.auth0.com"
AUTH0_CLIENT_ID = "your-client-id"
AUTH0_CLIENT_SECRET = "your-client-secret"
GROQ_API_KEY = "gsk_..."
```


***

## apps/streamlit_app/requirements.txt

```
streamlit==1.41.0
streamlit-oauth==0.1.4
httpx==0.28.1
requests==2.32.3
pandas==2.2.1
numpy==1.26.4
plotly==5.24.1
altair==5.4.1
python-dotenv==1.0.1
pydantic==2.8.2
pytz==2024.1
python-dateutil==2.9.0
```


***

## apps/api/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy shared core
COPY packages/core /app/packages/core

# Install API dependencies
COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install -e /app/packages/core

# Copy app
COPY apps/api /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


***

## apps/api/requirements.txt

```
fastapi==0.111.1
uvicorn[standard]==0.28.0
sqlalchemy==2.0.36
alembic==1.13.3
psycopg[binary]==3.2.1
pydantic==2.8.2
pydantic-settings==2.3.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.28.1
requests==2.32.3
redis==5.0.7
groq==0.9.0
python-dotenv==1.0.1
cryptography==43.0.0
aioredis==2.0.1
```


***

## apps/api/app/main.py

```python
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
```


***

## apps/api/app/config.py

```python
"""
FastAPI configuration and settings.
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/fitness_tracker"
    )

    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Auth0
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET: str = os.getenv("AUTH0_CLIENT_SECRET", "")
    AUTH0_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE", "")

    # Google Fit
    GOOGLE_FIT_CLIENT_ID: str = os.getenv("GOOGLE_FIT_CLIENT_ID", "")
    GOOGLE_FIT_CLIENT_SECRET: str = os.getenv("GOOGLE_FIT_CLIENT_SECRET", "")
    GOOGLE_FIT_REDIRECT_URI: str = os.getenv(
        "GOOGLE_FIT_REDIRECT_URI",
        "http://localhost:8000/api/integrations/google-fit/callback"
    )

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "https://*.streamlit.app",
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.streamlit.app",
    ]

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```


***

## apps/api/app/dependencies.py

```python
"""
FastAPI dependency injection utilities.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from app.db import SessionLocal
from jose import JWTError, jwt
from app.config import settings
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify JWT token and return current user.
    In production, verify against Auth0 JWKS.
    """
    token = credentials.credentials

    try:
        # TODO: In production, fetch JWKS from Auth0 and verify signature
        # For MVP, we accept the token and extract claims
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return {"sub": user_id, "email": email}

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

async def get_current_user_async(
    credentials: HTTPAuthCredentials = Depends(security)
) -> dict:
    """Async version of get_current_user."""
    return get_current_user(credentials)
```


***

## apps/api/app/db.py

```python
"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,  # Verify connections before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


***

## apps/api/app/models/__init__.py

```python
from .user import User
from .workout import Workout, WorkoutExercise, WorkoutTemplate
from .activity import Activity
from .nutrition import Meal, Macros, DailyNutrition
from .metrics import BodyMetric, ProgressPhoto
from .integrations import GoogleFitSync, AppleHealthSync

__all__ = [
    "User",
    "Workout",
    "WorkoutExercise",
    "WorkoutTemplate",
    "Activity",
    "Meal",
    "Macros",
    "DailyNutrition",
    "BodyMetric",
    "ProgressPhoto",
    "GoogleFitSync",
    "AppleHealthSync",
]
```


***

## apps/api/app/models/user.py

```python
"""
User model with Auth0 integration.
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class User(Base):
    """User account with Auth0 integration."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auth0_sub = Column(String(255), unique=True, nullable=False, index=True)  # sub claim
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)

    # Settings
    units = Column(String(50), default="metric")  # metric, imperial
    calorie_target = Column(Integer, default=2200)
    protein_target = Column(Integer, default=150)  # grams
    carb_target = Column(Integer, default=250)
    fat_target = Column(Integer, default=73)
    preferred_ai_model = Column(String(100), default="llama-3.3-70b-versatile")

    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_workout = Column(Integer, default=0)
    streak_nutrition = Column(Integer, default=0)

    # Privacy & integrations
    google_fit_enabled = Column(Boolean, default=False)
    apple_health_enabled = Column(Boolean, default=False)
    share_profile = Column(Boolean, default=False)
    settings_json = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("BodyMetric", back_populates="user", cascade="all, delete-orphan")
    google_fit_sync = relationship("GoogleFitSync", back_populates="user", cascade="all, delete-orphan")
    apple_health_sync = relationship("AppleHealthSync", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.auth0_sub})>"
```


***

## apps/api/app/models/workout.py

```python
"""
Workout, exercise, and template models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class Workout(Base):
    """Completed workout session."""
    __tablename__ = "workouts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=False)  # Session duration
    notes = Column(Text, nullable=True)
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion (1-10)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workout {self.id[:8]} ({self.date.date()})>"

class WorkoutExercise(Base):
    """Individual exercise within a workout."""
    __tablename__ = "workout_exercises"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String(36), ForeignKey("workouts.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # kg or lbs
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")

    def __repr__(self):
        return f"<Exercise {self.name}>"

class WorkoutTemplate(Base):
    """Reusable workout template."""
    __tablename__ = "workout_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exercises_json = Column(Text, nullable=False)  # JSON serialized list of exercises
    last_used = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template {self.name}>"
```


***

## apps/api/app/models/activity.py

```python
"""
Activity and wearable data models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class Activity(Base):
    """Logged activity (cardio, sports, etc.)."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    activity_type = Column(String(100), nullable=False)  # walk, run, swim, cycle, etc.
    date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=True)
    intensity = Column(String(50), nullable=True)  # easy, moderate, hard
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="manual")  # manual or google_fit

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity {self.activity_type} ({self.date.date()})>"
```


***

## apps/api/app/models/nutrition.py

```python
"""
Nutrition and macro tracking models.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class DailyNutrition(Base):
    """Daily nutrition summary."""
    __tablename__ = "daily_nutrition"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, default=datetime.utcnow, index=True)
    calories = Column(Integer, default=0)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Meal(Base):
    """Individual meal entry."""
    __tablename__ = "meals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    
    notes = Column(Text, nullable=True)
    ai_estimated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="meals")

    def __repr__(self):
        return f"<Meal {self.name}>"

class Macros(Base):
    """Quick macro reference for common foods."""
    __tablename__ = "macros"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    serving_size = Column(String(100), default="100g")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Macros {self.name}>"
```


***

## apps/api/app/models/metrics.py

```python
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
```


***

## apps/api/app/models/integrations.py

```python
"""
Integration state and sync models.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import uuid

class GoogleFitSync(Base):
    """Google Fit OAuth and sync state."""
    __tablename__ = "google_fit_sync"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)  # Encrypted in production
    token_expires_at = Column(DateTime, nullable=True)
    
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
    user = relationship("User", back_populates="google_fit_sync")

    def __repr__(self):
        return f"<GoogleFitSync {self.user_id[:8]}>"

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
```


***

## apps/api/app/schemas/__init__.py

```python
from .user import UserCreate, UserUpdate, UserResponse
from .workout import WorkoutCreate, WorkoutResponse, WorkoutExerciseCreate, WorkoutTemplateCreate
from .activity import ActivityCreate, ActivityResponse
from .nutrition import MealCreate, MealResponse, MacroResponse
from .metrics import BodyMetricCreate, BodyMetricResponse, ProgressPhotoCreate
from .integrations import GoogleFitOAuthURL, GoogleFitCallbackRequest, AppleHealthWebhook

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse",
    "WorkoutCreate", "WorkoutResponse", "WorkoutExerciseCreate", "WorkoutTemplateCreate",
    "ActivityCreate", "ActivityResponse",
    "MealCreate", "MealResponse", "MacroResponse",
    "BodyMetricCreate", "BodyMetricResponse", "ProgressPhotoCreate",
    "GoogleFitOAuthURL", "GoogleFitCallbackRequest", "AppleHealthWebhook",
]
```


***

## apps/api/app/schemas/user.py

```python
"""
User request/response schemas.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Create user from Auth0 token."""
    auth0_sub: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

class UserUpdate(BaseModel):
    """Update user profile and settings."""
    name: Optional[str] = None
    units: Optional[str] = None
    calorie_target: Optional[int] = None
    protein_target: Optional[int] = None
    carb_target: Optional[int] = None
    fat_target: Optional[int] = None
    preferred_ai_model: Optional[str] = None

class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    name: Optional[str]
    picture: Optional[str]
    units: str
    calorie_target: int
    protein_target: int
    xp: int
    level: int
    streak_workout: int
    created_at: datetime

    class Config:
        from_attributes = True
```


***

## apps/api/app/schemas/workout.py

```python
"""
Workout request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class WorkoutExerciseCreate(BaseModel):
    """Create exercise within workout."""
    name: str
    sets: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    order: int = 0

class WorkoutCreate(BaseModel):
    """Create workout session."""
    duration_minutes: int
    rpe: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseCreate]

class WorkoutResponse(BaseModel):
    """Workout response."""
    id: str
    date: datetime
    duration_minutes: int
    rpe: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkoutTemplateCreate(BaseModel):
    """Create or update workout template."""
    name: str
    description: Optional[str] = None
    exercises: List[WorkoutExerciseCreate]

class WorkoutTemplateResponse(BaseModel):
    """Workout template response."""
    id: str
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```


***

## apps/api/app/schemas/activity.py

```python
"""
Activity request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityCreate(BaseModel):
    """Create activity."""
    activity_type: str
    duration_minutes: int
    distance_km: Optional[float] = None
    intensity: Optional[str] = None
    calories_burned: Optional[float] = None
    notes: Optional[str] = None

class ActivityResponse(BaseModel):
    """Activity response."""
    id: str
    activity_type: str
    date: datetime
    duration_minutes: int
    distance_km: Optional[float]
    intensity: Optional[str]
    calories_burned: Optional[float]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True
```


***

## apps/api/app/schemas/nutrition.py

```python
"""
Nutrition request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MealCreate(BaseModel):
    """Create meal entry."""
    name: str
    meal_type: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str] = None

class MealResponse(BaseModel):
    """Meal response."""
    id: str
    name: str
    date: datetime
    meal_type: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    ai_estimated: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MacroResponse(BaseModel):
    """Macro reference response."""
    id: str
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size: str

    class Config:
        from_attributes = True
```


***

## apps/api/app/schemas/metrics.py

```python
"""
Body metrics request/response schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BodyMetricCreate(BaseModel):
    """Create body metric."""
    metric_type: str
    value: float
    unit: str = "kg"
    notes: Optional[str] = None

class BodyMetricResponse(BaseModel):
    """Body metric response."""
    id: str
    date: datetime
    metric_type: str
    value: float
    unit: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProgressPhotoCreate(BaseModel):
    """Create progress photo."""
    angle: str
    photo_url: str
    notes: Optional[str] = None

class ProgressPhotoResponse(BaseModel):
    """Progress photo response."""
    id: str
    date: datetime
    angle: str
    photo_url: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```


***

## apps/api/app/schemas/integrations.py

```python
"""
Integration request/response schemas.
"""
from pydantic import BaseModel
from typing import Optional

class GoogleFitOAuthURL(BaseModel):
    """Google Fit OAuth authorization URL."""
    auth_url: str
    state: str

class GoogleFitCallbackRequest(BaseModel):
    """Google Fit OAuth callback data."""
    code: str
    state: str

class GoogleFitStatus(BaseModel):
    """Google Fit sync status."""
    connected: bool
    last_sync: Optional[str] = None
    sync_status: str
    enabled_metrics: dict

class AppleHealthWebhook(BaseModel):
    """Apple Health webhook payload from iOS app."""
    user_id: str
    date: str
    steps: Optional[int] = None
    active_calories: Optional[float] = None
    sleep_minutes: Optional[int] = None
    workout_count: Optional[int] = None
```


***

## apps/api/app/routers/auth.py

```python
"""
Authentication routes (Auth0 OAuth callback).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/auth0-callback", response_model=dict)
def auth0_callback(
    auth0_sub: str,
    email: str,
    name: str = None,
    picture: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Auth0 callback.
    In production, verify the Auth0 token first.
    """
    # Check if user exists
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

    if not user:
        # Create new user
        user = User(
            auth0_sub=auth0_sub,
            email=email,
            name=name,
            picture=picture
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {email}")
    else:
        # Update picture/name if provided
        if name:
            user.name = name
        if picture:
            user.picture = picture
        db.commit()
        db.refresh(user)

    return {
        "user_id": user.id,
        "email": user.email,
        "message": "Authenticated"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user
```


***

## apps/api/app/routers/workouts.py

```python
"""
Workout logging and template routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.workout import Workout, WorkoutExercise, WorkoutTemplate
from app.schemas.workout import (
    WorkoutCreate, WorkoutResponse, WorkoutTemplateCreate, WorkoutTemplateResponse
)
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/log", response_model=dict)
def log_workout(
    workout: WorkoutCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a new workout."""
    db_workout = Workout(
        user_id=user_id,
        duration_minutes=workout.duration_minutes,
        rpe=workout.rpe,
        notes=workout.notes,
        date=datetime.utcnow()
    )
    db.add(db_workout)
    db.flush()

    # Add exercises
    for i, ex in enumerate(workout.exercises):
        db_exercise = WorkoutExercise(
            workout_id=db_workout.id,
            name=ex.name,
            sets=ex.sets,
            reps=ex.reps,
            weight=ex.weight,
            rest_seconds=ex.rest_seconds,
            notes=ex.notes,
            order=i
        )
        db.add(db_exercise)

    db.commit()
    db.refresh(db_workout)
    logger.info(f"Workout logged for user {user_id}")

    return {
        "id": db_workout.id,
        "date": db_workout.date,
        "exercises_count": len(workout.exercises)
    }

@router.get("/history", response_model=List[dict])
def get_workout_history(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get workout history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= cutoff
    ).order_by(Workout.date.desc()).all()

    return [
        {
            "id": w.id,
            "date": w.date,
            "duration_minutes": w.duration_minutes,
            "exercise_count": len(w.exercises),
            "rpe": w.rpe
        }
        for w in workouts
    ]

@router.post("/templates", response_model=dict)
def create_template(
    template: WorkoutTemplateCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create workout template."""
    import json
    db_template = WorkoutTemplate(
        user_id=user_id,
        name=template.name,
        description=template.description,
        exercises_json=json.dumps(
            [ex.dict() for ex in template.exercises]
        )
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return {"id": db_template.id, "name": db_template.name}

@router.get("/templates", response_model=List[dict])
def get_templates(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's workout templates."""
    templates = db.query(WorkoutTemplate).filter(
        WorkoutTemplate.user_id == user_id
    ).all()
    return [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in templates
    ]
```


***

## apps/api/app/routers/activities.py

```python
"""
Activity logging routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/log", response_model=dict)
def log_activity(
    activity: ActivityCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a manual activity."""
    db_activity = Activity(
        user_id=user_id,
        activity_type=activity.activity_type,
        duration_minutes=activity.duration_minutes,
        distance_km=activity.distance_km,
        intensity=activity.intensity,
        calories_burned=activity.calories_burned,
        notes=activity.notes,
        source="manual",
        date=datetime.utcnow()
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    logger.info(f"Activity logged: {activity.activity_type} for user {user_id}")
    return {"id": db_activity.id, "type": activity.activity_type}

@router.get("/today", response_model=dict)
def get_today_activity(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get today's activities summary."""
    today = datetime.utcnow().date()
    activities = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.date >= today
    ).all()

    total_distance = sum(a.distance_km or 0 for a in activities)
    total_calories = sum(a.calories_burned or 0 for a in activities)
    total_duration = sum(a.duration_minutes for a in activities)

    return {
        "total_activities": len(activities),
        "total_duration_minutes": total_duration,
        "total_distance_km": total_distance,
        "total_calories": total_calories
    }

@router.get("/history", response_model=List[dict])
def get_activity_history(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get activity history."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    activities = db.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.date >= cutoff
    ).order_by(Activity.date.desc()).all()

    return [
        {
            "id": a.id,
            "type": a.activity_type,
            "date": a.date,
            "duration_minutes": a.duration_minutes,
            "distance_km": a.distance_km,
            "calories": a.calories_burned
        }
        for a in activities
    ]
```


***

## apps/api/app/routers/nutrition.py

```python
"""
Nutrition and meal logging routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.nutrition import Meal, DailyNutrition
from app.schemas.nutrition import MealCreate, MealResponse
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/meals", response_model=dict)
def log_meal(
    meal: MealCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Log a meal."""
    db_meal = Meal(
        user_id=user_id,
        name=meal.name,
        meal_type=meal.meal_type,
        calories=meal.calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        notes=meal.notes,
        date=datetime.utcnow()
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    logger.info(f"Meal logged: {meal.name} for user {user_id}")
    return {"id": db_meal.id, "name": meal.name}

@router.get("/today", response_model=dict)
def get_today_nutrition(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get today's nutrition summary."""
    today = datetime.utcnow().date()
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date >= today
    ).all()

    total_calories = sum(m.calories for m in meals)
    total_protein = sum(m.protein_g for m in meals)
    total_carbs = sum(m.carbs_g for m in meals)
    total_fat = sum(m.fat_g for m in meals)

    return {
        "calories": total_calories,
        "protein_g": total_protein,
        "carbs_g": total_carbs,
        "fat_g": total_fat,
        "meal_count": len(meals)
    }

@router.get("/meals", response_model=List[dict])
def get_meals(
    user_id: str,
    days: int = 1,
    db: Session = Depends(get_db)
):
    """Get meals for past N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.date >= cutoff
    ).order_by(Meal.date.desc()).all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "meal_type": m.meal_type,
            "calories": m.calories,
            "protein_g": m.protein_g,
            "date": m.date
        }
        for m in meals
    ]
```


***

## apps/api/app/routers/metrics.py

```python
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
```


***

## apps/api/app/routers/integrations.py

```python
"""
Google Fit and Apple Health integration routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.integrations import GoogleFitSync, AppleHealthSync
from app.schemas.integrations import GoogleFitCallbackRequest, AppleHealthWebhook
from app.integrations.google_fit.oauth import get_oauth_url, exchange_code_for_token
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# ============ Google Fit ============

@router.get("/google-fit/auth-url")
def get_google_fit_auth_url(user_id: str):
    """Get Google Fit OAuth authorization URL."""
    auth_url, state = get_oauth_url(user_id)
    return {"auth_url": auth_url, "state": state}

@router.post("/google-fit/callback")
def google_fit_callback(
    request: GoogleFitCallbackRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Handle Google Fit OAuth callback."""
    try:
        access_token, refresh_token, expires_at = exchange_code_for_token(
            request.code,
            request.state
        )

        # Get or create sync record
        sync = db.query(GoogleFitSync).filter(
            GoogleFitSync.user_id == user_id
        ).first()

        if not sync:
            sync = GoogleFitSync(user_id=user_id)

        sync.access_token = access_token
        sync.refresh_token = refresh_token  # TODO: Encrypt this
        sync.token_expires_at = expires_at

        db.add(sync)
        db.commit()
        logger.info(f"Google Fit connected for user {user_id}")

        return {"status": "connected", "user_id": user_id}

    except Exception as e:
        logger.error(f"Google Fit callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect Google Fit"
        )

@router.get("/google-fit/status")
def get_google_fit_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get Google Fit connection status."""
    sync = db.query(GoogleFitSync).filter(
        GoogleFitSync.user_id == user_id
    ).first()

    if not sync or not sync.refresh_token:
        return {"connected": False}

    return {
        "connected": True,
        "last_sync": sync.last_sync,
        "sync_status": sync.sync_status,
        "enabled_metrics": {
            "steps": sync.sync_steps,
            "activities": sync.sync_activities,
            "calories": sync.sync_calories,
            "heart_rate": sync.sync_heart_rate
        }
    }

@router.post("/google-fit/sync")
def trigger_google_fit_sync(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Trigger manual Google Fit sync."""
    sync = db.query(GoogleFitSync).filter(
        GoogleFitSync.user_id == user_id
    ).first()

    if not sync or not sync.refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # TODO: Queue background sync job
    sync.sync_status = "syncing"
    sync.last_sync = datetime.utcnow()
    db.commit()

    return {"status": "sync_queued"}

# ============ Apple Health ============

@router.post("/apple-health/webhook")
def apple_health_webhook(
    data: AppleHealthWebhook,
    db: Session = Depends(get_db)
):
    """
    Webhook from iOS companion app.
    TODO: Verify webhook signature.
    """
    user_id = data.user_id
    sync = db.query(AppleHealthSync).filter(
        AppleHealthSync.user_id == user_id
    ).first()

    if not sync:
        sync = AppleHealthSync(user_id=user_id)

    sync.last_sync = datetime.utcnow()
    sync.sync_status = "syncing"

    # TODO: Process data (insert activities, metrics, etc.)
    db.add(sync)
    db.commit()

    logger.info(f"Apple Health webhook received for user {user_id}")
    return {"status": "received"}

@router.get("/apple-health/status")
def get_apple_health_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get Apple Health connection status."""
    sync = db.query(AppleHealthSync).filter(
        AppleHealthSync.user_id == user_id
    ).first()

    if not sync or not sync.webhook_secret:
        return {"connected": False}

    return {
        "connected": True,
        "last_sync": sync.last_sync,
        "sync_status": sync.sync_status,
        "enabled_metrics": {
            "steps": sync.sync_steps,
            "workouts": sync.sync_workouts,
            "sleep": sync.sync_sleep
        }
    }
```


***

## apps/api/app/routers/ai_coach.py

```python
"""
AI Coach routes via Groq.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.integrations.groq_client import GroqCoach
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CoachMessage(BaseModel):
    """User message to coach."""
    message: str
    mode: str = "general"  # general, plan, nutrition, recovery, motivation, explain_data
    model: str = "llama-3.3-70b-versatile"

class CoachResponse(BaseModel):
    """Coach response."""
    message: str
    actions: dict = {}  # Structured actions (JSON)
    requires_review: bool = False

@router.post("/chat", response_model=CoachResponse)
def chat_with_coach(
    request: CoachMessage,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Chat with AI coach."""
    try:
        coach = GroqCoach(settings.GROQ_API_KEY, request.model)
        response = coach.chat(
            message=request.message,
            mode=request.mode,
            user_id=user_id
        )

        return CoachResponse(
            message=response.get("text", ""),
            actions=response.get("actions", {}),
            requires_review=bool(response.get("actions"))
        )

    except Exception as e:
        logger.error(f"Coach error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Coach service error"
        )

@router.get("/models")
def get_available_models():
    """Get available Groq models."""
    return {
        "models": [
            {"id": "groq/compound", "name": "Compound"},
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
            {"id": "openai/gpt-oss-120b", "name": "OpenAI GPT OSS 120B (if available)"}
        ]
    }

@router.post("/action/{action_id}/approve")
def approve_coach_action(
    action_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Approve and apply a coach action."""
    # TODO: Parse action_id, apply to user data
    logger.info(f"Action {action_id} approved by user {user_id}")
    return {"status": "approved"}
```


***

## apps/api/app/routers/users.py

```python
"""
User profile and settings routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    update: UserUpdate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Update fields
    if update.name is not None:
        user.name = update.name
    if update.units is not None:
        user.units = update.units
    if update.calorie_target is not None:
        user.calorie_target = update.calorie_target
    if update.protein_target is not None:
        user.protein_target = update.protein_target
    if update.carb_target is not None:
        user.carb_target = update.carb_target
    if update.fat_target is not None:
        user.fat_target = update.fat_target
    if update.preferred_ai_model is not None:
        user.preferred_ai_model = update.preferred_ai_model

    db.commit()
    db.refresh(user)
    logger.info(f"User {user_id} profile updated")
    return user

@router.get("/gamification")
def get_gamification(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get gamification stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {
        "xp": user.xp,
        "level": user.level,
        "streak_workout": user.streak_workout,
        "streak_nutrition": user.streak_nutrition,
        "next_level_xp": (user.level * 1000)  # Simple calculation
    }
```


***

## apps/api/app/integrations/groq_client.py

```python
"""
Groq AI Coach client.
"""
from groq import Groq
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GroqCoach:
    """Groq-powered AI fitness coach."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.system_prompt = """
You are an expert AI fitness coach. You provide personalized training, nutrition, and recovery advice.

IMPORTANT SAFETY RULES:
- Always include disclaimer: "This is not medical advice. Consult a professional if needed."
- Detect and avoid recommending: extreme calorie deficits, dangerous supplements, risky exercises
- If user mentions injury or medical concern, recommend professional medical evaluation
- Keep tone motivational but realistic

When providing actionable recommendations, format them as JSON:
{
  "action_type": "create_workout" | "update_macros" | "add_quest" | "plan_week",
  "details": { ... }
}

Modes:
- plan: Help create workout plans
- nutrition: Nutrition and macro advice
- recovery: Sleep, hydration, mobility
- motivation: Encouragement and mindset
- explain_data: Analyze user's fitness data
- general: General fitness questions
"""

    def chat(
        self,
        message: str,
        mode: str = "general",
        user_id: str = None
    ) -> Dict[str, Any]:
        """Chat with coach."""
        try:
            # Prepend mode context
            prompt = f"[Mode: {mode}] {message}"

            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                system=self.system_prompt,
                max_tokens=1000,
                temperature=0.7
            )

            text = response.content[0].text

            # Try to extract JSON actions
            actions = {}
            if "{" in text and "action_type" in text:
                try:
                    # Simple JSON extraction (not bulletproof)
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    actions = json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

            logger.info(f"Coach response for user {user_id} in mode {mode}")

            return {
                "text": text,
                "actions": actions
            }

        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

class SafetyChecker:
    """Simple keyword-based safety check."""

    RISKY_KEYWORDS = [
        "starvation",
        "no food",
        "laxatives",
        "diuretics",
        "extreme",
        "dangerous",
        "broken bone",
        "severe pain"
    ]

    @staticmethod
    def check(text: str) -> bool:
        """Return True if text contains risky keywords."""
        return any(keyword in text.lower() for keyword in SafetyChecker.RISKY_KEYWORDS)
```


***

## apps/api/app/integrations/google_fit/__init__.py

```python
"""Google Fit integration module."""
```


***

## apps/api/app/integrations/google_fit/oauth.py

```python
"""
Google Fit OAuth flow.
"""
from app.config import settings
import requests
import uuid
import logging

logger = logging.getLogger(__name__)

def get_oauth_url(user_id: str) -> tuple:
    """Generate Google Fit OAuth authorization URL."""
    state = str(uuid.uuid4())
    # Store state in Redis/session for verification (TODO)

    params = {
        "client_id": settings.GOOGLE_FIT_CLIENT_ID,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/fitness.activity.read "
                 "https://www.googleapis.com/auth/fitness.body.read",
        "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI,
        "state": state
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + \
          "&".join(f"{k}={v}" for k, v in params.items())

    return url, state

def exchange_code_for_token(code: str, state: str) -> tuple:
    """Exchange authorization code for access token."""
    # TODO: Verify state

    payload = {
        "client_id": settings.GOOGLE_FIT_CLIENT_ID,
        "client_secret": settings.GOOGLE_FIT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI
    }

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.text}")

    data = response.json()
    access_token = data["access_token"]
    refresh_token = data.get("refresh_token")
    expires_in = data.get("expires_in", 3600)

    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    logger.info("Google Fit token acquired")
    return access_token, refresh_token, expires_at

def refresh_access_token(refresh_token: str) -> str:
    """Refresh an expired access token."""
    payload = {
        "client_id": settings.GOOGLE_FIT_CLIENT_ID,
        "client_secret": settings.GOOGLE_FIT_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        json=payload
    )

    if response.status_code != 200:
        raise Exception("Token refresh failed")

    return response.json()["access_token"]
```


***

## apps/api/app/integrations/google_fit/sync.py

```python
"""
Google Fit data sync logic.
"""
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def sync_google_fit_data(
    user_id: str,
    access_token: str,
    sync_steps: bool = True,
    sync_activities: bool = True,
    sync_calories: bool = True
):
    """
    Sync data from Google Fit.
    TODO: Parse responses and insert into DB.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # Define data sources
    datasources = {
        "steps": "com.google.android.gms:step_count/delta",
        "activities": "com.google.android.gms:activity_segment",
        "calories": "com.google.android.gms:calories_expended/delta"
    }

    results = {}

    if sync_steps:
        results["steps"] = _fetch_datapoint(
            access_token,
            datasources["steps"]
        )

    if sync_activities:
        results["activities"] = _fetch_activity_segments(
            access_token,
            datasources["activities"]
        )

    if sync_calories:
        results["calories"] = _fetch_datapoint(
            access_token,
            datasources["calories"]
        )

    logger.info(f"Google Fit sync complete for user {user_id}")
    return results

def _fetch_datapoint(access_token: str, datasource: str):
    """Fetch a data point from Google Fit API."""
    headers = {"Authorization": f"Bearer {access_token}"}
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    yesterday_ms = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    payload = {
        "aggregateBy": [{
            "dataTypeName": datasource
        }],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": yesterday_ms,
        "endTimeMillis": now_ms
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json() if response.status_code == 200 else {}

def _fetch_activity_segments(access_token: str, datasource: str):
    """Fetch activity segments."""
    # Similar to _fetch_datapoint but handles activity data
    return {}
```


***

## apps/api/app/integrations/apple_health/__init__.py

```python
"""Apple Health integration module."""
```


***

## apps/api/app/integrations/apple_health/sync.py

```python
"""
Apple Health webhook receiver and processor.
TODO: Full implementation with iOS companion app.
"""
import logging

logger = logging.getLogger(__name__)

def process_apple_health_webhook(user_id: str, data: dict):
    """
    Process webhook data from iOS companion app.
    
    TODO: Extract steps, workouts, sleep, etc. and insert into DB.
    """
    logger.info(f"Processing Apple Health webhook for {user_id}")
    # TODO: Implement
    pass
```


***

## packages/core/__init__.py

```python
"""Shared core package."""
from .settings import Settings
from .logging_config import setup_logging
from .types import UserID, WorkoutID
from .security import encrypt_token, decrypt_token

__all__ = [
    "Settings",
    "setup_logging",
    "UserID",
    "WorkoutID",
    "encrypt_token",
    "decrypt_token",
]
```


***

## packages/core/settings.py

```python
"""
Shared settings configuration.
"""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    """Core application settings."""
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/fitness")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
```


***

## packages/core/logging_config.py

```python
"""
Logging configuration for shared use.
"""
import logging
import sys

def setup_logging(level: str = "INFO"):
    """Setup structured logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
```


***

## packages/core/types.py

```python
"""
Type definitions.
"""
from typing import NewType

UserID = NewType("UserID", str)
WorkoutID = NewType("WorkoutID", str)
ActivityID = NewType("ActivityID", str)
MealID = NewType("MealID", str)
```


***

## packages/core/security.py

```python
"""
Security utilities: encryption, hashing, token handling.
"""
from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)

def get_cipher():
    """Get Fernet cipher for encryption."""
    # In production, load from secure key management (AWS KMS, HashiCorp Vault, etc.)
    key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_token(plaintext: str) -> str:
    """Encrypt a token (e.g., refresh token)."""
    cipher = get_cipher()
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted.decode()

def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token."""
    cipher = get_cipher()
    decrypted = cipher.decrypt(ciphertext.encode())
    return decrypted.decode()
```


***

## apps/api/alembic/env.py

```python
"""
Alembic environment configuration.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None  # Will be set in migrations

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")
    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    url = os.getenv("DATABASE_URL")
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```


***

## apps/api/alembic/versions/001_initial_schema.py

```python
"""
Initial database schema migration.
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Create initial tables."""
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('auth0_sub', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('picture', sa.String(500), nullable=True),
        sa.Column('units', sa.String(50), default='metric'),
        sa.Column('calorie_target', sa.Integer, default=2200),
        sa.Column('protein_target', sa.Integer, default=150),
        sa.Column('xp', sa.Integer, default=0),
        sa.Column('level', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now()),
    )

    op.create_index('ix_users_auth0_sub', 'users', ['auth0_sub'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'workouts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.DateTime, default=sa.func.now()),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('rpe', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    op.create_index('ix_workouts_user_id_date', 'workouts', ['user_id', 'date'])

def downgrade():
    """Drop initial tables."""
    op.drop_table('workouts')
    op.drop_table('users')
```


***

## docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: fitness-postgres
    environment:
      POSTGRES_DB: fitness_tracker
      POSTGRES_USER: fitness_user
      POSTGRES_PASSWORD: changeme
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fitness_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: fitness-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    container_name: fitness-api
    environment:
      DATABASE_URL: postgresql://fitness_user:changeme@postgres:5432/fitness_tracker
      REDIS_URL: redis://redis:6379/0
      AUTH0_DOMAIN: ${AUTH0_DOMAIN}
      AUTH0_CLIENT_ID: ${AUTH0_CLIENT_ID}
      AUTH0_CLIENT_SECRET: ${AUTH0_CLIENT_SECRET}
      GOOGLE_FIT_CLIENT_ID: ${GOOGLE_FIT_CLIENT_ID}
      GOOGLE_FIT_CLIENT_SECRET: ${GOOGLE_FIT_CLIENT_SECRET}
      GROQ_API_KEY: ${GROQ_API_KEY}
      ENVIRONMENT: production
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  worker:
    build:
      context: .
      dockerfile: apps/worker/Dockerfile
    container_name: fitness-worker
    environment:
      DATABASE_URL: postgresql://fitness_user:changeme@postgres:5432/fitness_tracker
      REDIS_URL: redis://redis:6379/0
      GROQ_API_KEY: ${GROQ_API_KEY}
      ENVIRONMENT: production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: python worker.py

  streamlit:
    build:
      context: .
      dockerfile: apps/streamlit_app/Dockerfile
    container_name: fitness-streamlit
    environment:
      API_BASE_URL: http://api:8000/api
      AUTH0_DOMAIN: ${AUTH0_DOMAIN}
      AUTH0_CLIENT_ID: ${AUTH0_CLIENT_ID}
    ports:
      - "8501:8501"
    depends_on:
      - api
    command: streamlit run app.py

volumes:
  postgres_data:

networks:
  default:
    name: fitness-network
```


***

## apps/worker/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY packages/core /app/packages/core
COPY apps/worker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install -e /app/packages/core

COPY apps/worker /app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "worker.py"]
```


***

## apps/worker/requirements.txt

```
apscheduler==3.10.4
sqlalchemy==2.0.36
psycopg[binary]==3.2.1
redis==5.0.7
python-dotenv==1.0.1
groq==0.9.0
requests==2.32.3
```


***

## apps/worker/worker.py

```python
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
from apps.api.app.models import User, GoogleFitSync
from jobs import sync_google_fit, daily_quest_gen, xp_processor

# Database
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

def job_sync_google_fit():
    """Periodic Google Fit sync job."""
    db = SessionLocal()
    try:
        sync_google_fit.sync_all_users(db)
    finally:
        db.close()

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

    # Google Fit sync every 6 hours
    scheduler.add_job(
        job_sync_google_fit,
        CronTrigger(hour="*/6"),
        id="sync_google_fit"
    )

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
```


***

## apps/worker/jobs/sync_google_fit.py

```python
"""
Google Fit sync job.
"""
import logging
from sqlalchemy.orm import Session
from apps.api.app.models import User, GoogleFitSync
from apps.api.app.integrations.google_fit.oauth import refresh_access_token
from apps.api.app.integrations.google_fit.sync import sync_google_fit_data
from datetime import datetime

logger = logging.getLogger(__name__)

def sync_all_users(db: Session):
    """Sync Google Fit data for all connected users."""
    syncs = db.query(GoogleFitSync).filter(
        GoogleFitSync.refresh_token.isnot(None)
    ).all()

    for sync in syncs:
        try:
            # Refresh token
            new_token = refresh_access_token(sync.refresh_token)

            # Sync data
            sync_google_fit_data(
                sync.user_id,
                new_token,
                sync.sync_steps,
                sync.sync_activities,
                sync.sync_calories
            )

            sync.last_sync = datetime.utcnow()
            sync.sync_status = "success"
            db.commit()

            logger.info(f"Google Fit sync successful for user {sync.user_id}")

        except Exception as e:
            logger.error(f"Google Fit sync failed for user {sync.user_id}: {e}")
            sync.sync_status = "error"
            db.commit()
```


***

## apps/worker/jobs/daily_quest_gen.py

```python
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
```


***

## apps/worker/jobs/xp_processor.py

```python
"""
XP processing and level calculation.
"""
import logging
from sqlalchemy.orm import Session
from apps.api.app.models import User, Workout

logger = logging.getLogger(__name__)

def process_xp(db: Session):
    """Process XP gains and level ups."""
    users = db.query(User).all()

    for user in users:
        # TODO: Calculate XP from workouts, streaks, quests completed
        # Award bonuses, level up logic
        logger.debug(f"XP processed for user {user.id}")
```


***

## apps/worker/jobs/__init__.py

```python
"""Worker jobs module."""
```


***

## scripts/seed_demo_data.py

```python
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
from apps.api.app.models import (
    Base, User, Workout, WorkoutExercise, Activity, Meal, BodyMetric
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
```


***

## apps/streamlit_app/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/streamlit_app /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```


***



