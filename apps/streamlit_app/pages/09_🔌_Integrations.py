import streamlit as st
import requests
import pytz
from dateutil import parser
from datetime import datetime

def format_sync_time(dt_str):
    """Convert UTC string to IST formatted string."""
    if not dt_str:
        return "Never"
    try:
        # Parse if string
        if isinstance(dt_str, str):
            dt = parser.parse(dt_str)
        else:
            dt = dt_str
            
        # Ensure UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
            
        # Convert to IST
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = dt.astimezone(ist)
        
        return dt_ist.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return str(dt_str)[:19]

st.set_page_config(page_title="Integrations", page_icon="🔌", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🔌 Integrations")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Fitbit
st.subheader("⌚ Fitbit")

try:
    # 1. Check Status
    response = requests.get(
        f"{get_api_base()}/integrations/fitbit/status",
        params={"user_id": st.session_state.user_id},
        headers=get_headers()
    )
    
    # 2. Handle Status
    if response.status_code == 200:
        status = response.json()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if status.get("connected"):
                st.success("✅ Connected")
                st.caption(f"Last sync: {format_sync_time(status.get('last_sync'))}")
            else:
                st.warning("⚠️ Not connected")
                
        with col2:
            if status.get("connected"):
                if st.button("🔄 Sync Now"):
                    with st.spinner("Syncing with Fitbit..."):
                        sync_resp = requests.post(f"{get_api_base()}/integrations/fitbit/sync", params={"user_id": st.session_state.user_id}, headers=get_headers())
                        if sync_resp.status_code == 200:
                            st.success("Synced!")
                            st.rerun()
                        else:
                            st.error("Sync failed")
        
        with col3:
            if not status.get("connected"):
                # Fetch Auth URL
                try:
                    auth_resp = requests.get(f"{get_api_base()}/integrations/fitbit/auth-url", params={"user_id": st.session_state.user_id}, headers=get_headers())
                    if auth_resp.status_code == 200:
                        url = auth_resp.json().get("auth_url")
                        st.link_button("🔗 Connect Fitbit", url)
                    else:
                        st.error("Setup required")
                except:
                    st.error("Config error")
                    
        st.divider()
        
        # Display Synced Data (Sleek UI)
        if status.get("connected") and status.get("sync_status") != "idle":
            st.markdown("### 📊 Latest Synced Data")
            
            # Parse the status string if it contains metrics (format: "Steps: X, Cals: Y")
            # If standard idle/syncing, we fallback
            sync_str = status.get("sync_status", "")
            
            steps_val = "--"
            cals_val = "--"
            
            if "Steps:" in sync_str:
                try:
                    parts = sync_str.split(", ")
                    for p in parts:
                        if "Steps:" in p: steps_val = p.split(":")[1].strip()
                        if "Cals:" in p: cals_val = p.split(":")[1].strip()
                except:
                    pass
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("👣 Steps", steps_val)
            with m2:
                st.metric("🔥 Calories Burned", cals_val)
            with m3:
                st.metric("✅ Status", "Active")
                
        elif status.get("connected"):
             st.info("Sync to see your latest stats!")

        st.divider()
        st.write("**Sync Config**")
        c1, c2, c3 = st.columns(3)
        with c1: st.toggle("Sync Steps", value=True, disabled=True)
        with c2: st.toggle("Sync Calories", value=True, disabled=True)
        with c3: st.toggle("Sync Sleep", value=True, disabled=True)

    elif response.status_code == 501:
         st.info("Fitbit integration is not configured on the server.")
    else:
        st.error("Failed to load Fitbit status")

    # 3. Check for Callback Code in URL
    query_params = st.query_params
    if "code" in query_params and "state" in query_params:
        code = query_params["code"]
        state = query_params["state"]
        
        if state == st.session_state.user_id:
            with st.spinner("Completing connection..."):
                cb_resp = requests.post(
                    f"{get_api_base()}/integrations/fitbit/callback",
                    json={"code": code, "state": state},
                    headers=get_headers()
                )
                if cb_resp.status_code == 200:
                    st.success("Fitbit connected successfully!")
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error(f"Connection failed: {cb_resp.text}")

except Exception as e:
    st.error(f"Integration error: {e}")

st.divider()

# Apple Health
st.subheader("🍎 Apple Health")

try:
    response = requests.get(
        f"{get_api_base()}/integrations/apple-health/status",
        params={"user_id": st.session_state.user_id},
        headers=get_headers()
    )

    if response.status_code == 200:
        status = response.json()

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if status.get("connected"):
                st.success("✅ Connected")
                st.caption(f"Last sync: {format_sync_time(status.get('last_sync'))}")
            else:
                st.warning("⚠️ Not connected")

        with col2:
            st.write("")

        with col3:
            if st.button("Download App", key="apple_app"):
                st.info("Download iOS companion app from App Store")

        st.divider()

        # Metric toggles
        st.write("**Sync Metrics**")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.checkbox("Steps", value=status.get("enabled_metrics", {}).get("steps", True), key="apple_steps")

        with col2:
            st.checkbox("Workouts", value=status.get("enabled_metrics", {}).get("workouts", True), key="apple_workouts")

        with col3:
            st.checkbox("Sleep", value=status.get("enabled_metrics", {}).get("sleep", True), key="apple_sleep")

except Exception as e:
    st.error(f"Failed to load Apple Health status: {e}")

st.divider()

# API Documentation
with st.expander("📚 API Documentation"):
    st.markdown("""
    ### Webhook URLs for integrations:
    
    **Health Connect Sync:**
    `POST /integrations/health-connect/sync`
    """)

render_sidebar_footer()
    