# EpochOne - AI Fitness Tracker 🏋️‍♂️⌚🤖

EpochOne is a comprehensive AI-powered fitness tracking application designed to centralize your health data. It features a modern Streamlit frontend, a robust FastAPI backend, and seamless integrations with popular wearables like Fitbit and Apple Health. At its core is an intelligent AI Coach (powered by Groq) that provides personalized health insights and motivation.

**Status**: MVP Complete (Web, API, Worker, Database) with Docker Compose deployment.

---

## 🚀 Features

### Core Tracking
- **Workouts**: Log strength training with exercises, sets, reps, weight, RPE, and rest timers. Save and reuse workout templates.
- **Activities**: Track cardio, sports, and other activities. Sync automatically from wearables.
- **Nutrition**: Log daily meals and track macronutrients (Protein, Carbs, Fat) and calories against your goals.
- **Body Metrics**: Monitor weight, body fat %, measurements (waist, chest, etc.), and BMI trends.
- **Wellness**: Track daily holistic metrics including Sleep Quality, Stress Levels, Soreness, and Energy.
- **Data Export**: Full GDPR-compliant export of all your data (Profile, Workouts, Nutrition, Metrics, Wellness) as a ZIP file.

### 🔌 Integrations
- **Fitbit**: Full OAuth 2.0 integration. Syncs **steps**, **calories burned**, **activity intensity**, and **sleep** data directly to your dashboard.
- **Apple Health**: Webhook-based integration support for iOS companion apps.
- **Health Connect**: Android integration support.
- **Groq AI Coach**: Personal health assistant running on Llama 3/3.3 models via Groq. Provides actionable advice based on your real-time data.

### 🤖 AI Coach
- **Context-Aware**: The coach knows your latest workouts, nutrition synced from Fitbit, and goals.
- **Modes**:
  - **Plan**: Generate workout routines.
  - **Nutrition**: Get meal suggestions based on remaining macros.
  - **Recovery**: Tips to improve sleep and reduce fatigue.
  - **Motivation**: Hype messages to keep you consistent.
- **Safety**: Built-in guardrails for safe health advice.

### 🎮 Gamification
- **XP System**: Earn XP for logging workouts, meals, and completing synchronization.
- **Levels**: Level up as you stay consistent.
- **Streaks**: Track diverse streaks (Workout, Nutrition, Sync).
- **Daily Quests**: AI-generated daily challenges (e.g., "Walk 5000 steps", "Eat 20g protein").

### 🎨 UI & UX
- **Live Unit Toggles**: Instantly switch between Metric (kg/cm) and Imperial (lbs/in) units globally.
- **Onboarding Flow**: Interactive setup wizard for new users to set goals and profile details.
- **Dashboard**: Real-time "at a glance" view of your daily stats and AI Coach tips.

### 🔐 Authentication & Security
- **Auth0 / Google Login**: Secure OIDC authentication using standard OAuth2 flow.
- **Ephemeral Sessions**: Designed for security and stability; sessions clear on refresh.
- **User Segregation**: Complete data isolation between users.
- **Encrypted Tokens**: OAuth tokens (Fitbit) are encrypted at rest.

---

## 🛠️ Architecture

The project is built as a set of Dockerized microservices:

1.  **Frontend (`apps/streamlit_app`)**: A responsive UI built with Python Streamlit.
2.  **API (`apps/api`)**: FastAPI backend handling business logic, DB access, and OAuth flows.
3.  **Worker (`apps/worker`)**: Background process for scheduled synchronization jobs and XP processing.
4.  **Database**: PostgreSQL 15 for relational data.
5.  **Cache**: Redis 7 for session management and job queues.

---

## ⚙️ Setup & Deployment

### Prerequisite
- Docker & Docker Compose
- API Keys for Auth0, Fitbit, and Groq.

### 1. clone the repository
```bash
git clone https://github.com/sambitcodes/EpochOne.git
cd EpochOne
```

### 2. Configure Environment (`.env`)
Copy the example environment file and fill in your secrets.
```bash
cp apps/api/.env.example .env
```
**Required Secrets in `.env`**:
- `DATABASE_URL`: `postgresql+psycopg://fitness_user:changeme@postgres:5432/fitness_tracker`
- `REDIS_URL`: `redis://redis:6379/0`
- `SECRET_KEY`: Generate a random string.
- `GROQ_API_KEY`: Get from [Groq Console](https://console.groq.com).
- `AUTH0_DOMAIN`, `CLIENT_ID`, `CLIENT_SECRET`: Get from [Auth0](https://auth0.com).
- `FITBIT_CLIENT_ID`, `FITBIT_CLIENT_SECRET`, `FITBIT_REDIRECT_URI`: Get from [dev.fitbit.com](https://dev.fitbit.com).

### 3. Run with Docker Compose
```bash
docker-compose up --build -d
```
The app will be available at:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

### 4. Initialize Database
Apply migrations to set up the schema.
```bash
docker-compose exec api alembic upgrade head
```
(Optional) Seed demo data:
```bash
docker-compose exec api python scripts/seed_demo_data.py
```

---

## ⌚ Fitbit Setup Guide

1.  Go to **[dev.fitbit.com](https://dev.fitbit.com)** -> Manage -> Register an App.
2.  **OAuth 2.0 Application Type**: Server.
3.  **Callback URL**: `http://localhost:8501` (Important: The app handles the callback on the home page).
4.  **Default Access Type**: Read & Write.
5.  Copy `Client ID` and `Client Secret` to your `.env` file.
6.  Restart containers: `docker-compose up -d`.

---

## 🗺️ Roadmap

- ✅ **MVP Core**: Workouts, Nutrition, Body Metrics.
- ✅ **Gamification**: XP, Levels, Streaks.
- ✅ **AI Intergration**: Groq-powered Contextual Coach.
- ✅ **Fitbit Integration**: Complete OAuth flow & data sync.
- ⏳ **Mobile App**: Companion app for iOS/Android (via Flutter or React Native).
- ⏳ **Advanced Trend Analytics**: 1RM calculation, Volume trends, Progress Photo comparison.
- 🔮 **Social**: Friend leaderboards and challenges.

---

## 📄 License
MIT License.

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
