import requests
import base64
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FitbitClient:
    """Client for interacting with Fitbit API."""
    
    AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    API_BASE = "https://api.fitbit.com/1"
    
    def __init__(self):
        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8501")
        
    def get_auth_url(self, state: str) -> str:
        """Generate authorization URL."""
        if not self.client_id:
            raise ValueError("Fitbit Client ID not configured")
            
        scope = "activity nutrition heartrate sleep profile"
        return (
            f"{self.AUTH_URL}?response_type=code&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}&scope={scope}&state={state}"
        )
        
    def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Fitbit credentials not configured")
            
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "clientId": self.client_id,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            logger.error(f"Fitbit token exchange failed: {response.text}")
            raise Exception("Failed to exchange code for token")
            
        return response.json()
        
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token."""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception("Failed to refresh token")
            
        return response.json()

    def get_data(self, access_token: str, endpoint: str) -> dict:
        """Fetch data from Fitbit API."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.API_BASE}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"API request failed: {response.status_code}")
