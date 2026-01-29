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
