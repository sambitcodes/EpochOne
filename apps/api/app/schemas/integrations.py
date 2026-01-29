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

class FitbitOAuthURL(BaseModel):
    """Fitbit OAuth authorization URL."""
    auth_url: str
    state: str

class FitbitCallbackRequest(BaseModel):
    """Fitbit OAuth callback data."""
    code: str
    state: str

class FitbitStatus(BaseModel):
    """Fitbit sync status."""
    connected: bool
    last_sync: Optional[str] = None
    sync_status: str
    enabled_metrics: dict