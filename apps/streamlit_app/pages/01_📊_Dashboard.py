"""Dashboard home page."""
import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any
import sys
import os

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from ui.components import metric_card, stat_box, section_header, card_container
from ui.layout import two_column_layout, three_column_layout, render_sidebar, render_sidebar_footer
from ui.styles import apply_theme

apply_theme()
render_sidebar()

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
    st.session_state.user = None

if not st.session_state.access_token:
    st.switch_page("Home.py")


from utils import get_api_base

# ============ API Helpers ============

# get_api_base is imported from utils

def get_headers():
    """Get auth headers."""
    return {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }

# ============ Data Fetching ============

# @st.cache_data(ttl=300)
def fetch_today_summary() -> Dict[str, Any]:
    """Fetch today's summary (IST)."""
    # IST = UTC + 5:30
    today_iso = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{get_api_base()}/activities/today",
            params={"user_id": st.session_state.user_id or "dev_user", "date_str": today_iso},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch activities: {e}")
    return {}

# @st.cache_data(ttl=300)
def fetch_nutrition_today() -> Dict[str, Any]:
    """Fetch today's nutrition (IST)."""
    today_iso = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{get_api_base()}/nutrition/today",
            params={"user_id": st.session_state.user_id or "dev_user", "date_str": today_iso},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch nutrition: {e}")
    return {}

# @st.cache_data(ttl=300)
def fetch_gamification() -> Dict[str, Any]:
    """Fetch gamification stats."""
    try:
        response = requests.get(
            f"{get_api_base()}/users/gamification",
            params={"user_id": st.session_state.user_id or "dev_user"},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch gamification: {e}")
    return {}

# @st.cache_data(ttl=300)
def fetch_workout_today() -> Dict[str, Any]:
    """Fetch today's workout (IST)."""
    today_iso = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{get_api_base()}/workouts/today",
            params={"user_id": st.session_state.user_id or "dev_user", "date_str": today_iso},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch workout: {e}")
    return {}   

# ============ Page Content ============

from datetime import timedelta
# IST Calculation
now_utc = datetime.utcnow()
now_ist = now_utc + timedelta(hours=5, minutes=30)
today_iso = now_ist.strftime("%Y-%m-%d")

st.title("📊 Dashboard")
st.markdown(f"Welcome back! Today is **{now_ist.strftime('%d-%m-%Y')}** (Time: {now_ist.strftime('%H:%M:%S')})")
st.divider()

import plotly.graph_objects as go

# ... (keep existing imports)

# @st.cache_data(ttl=300)
def fetch_wellness_today(metric_type: str) -> float:
    """Fetch today's wellness metric sum (IST)."""
    today_iso = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{get_api_base()}/wellness/logs",
            params={"user_id": st.session_state.user_id or "dev_user", "metric_type": metric_type, "date_str": today_iso},
            headers=get_headers()
        )
        if response.status_code == 200:
            logs = response.json()
            return sum(l.get('value_primary', 0) for l in logs)
    except Exception as e:
        st.error(f"Failed to fetch {metric_type}: {e}")
# @st.cache_data(ttl=60)
def fetch_daily_summary() -> Dict[str, Any]:
    """Fetch consolidated daily summary."""
    try:
        response = requests.get(
            f"{get_api_base()}/metrics/daily-summary",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return {}

# ... (existing functions)

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

activities = fetch_today_summary()
nutrition = fetch_nutrition_today()
summary = fetch_daily_summary() # New Source of Truth for Cals
gamification = fetch_gamification()
workout = fetch_workout_today()
water_ml = fetch_wellness_today("hydration")

with col1:
    metric_card(
        "Steps",
        f"{activities.get('total_steps', 0):,}", # Use total_steps (Fitbit + Manual)
        f"Goal: {st.session_state.user.get('step_goal', 10000)}",
        "👟",
        "#38bdf8"
    )

with col2:
    # Use consolidated summary
    net = summary.get("net_balance", 0)
    status = summary.get("status", "Deficit")
    color = "#10b981" if status == "Deficit" and net > 0 else "#ef4444" 
    
    metric_card(
        "Net Balance",
        f"{abs(net):.0f}",
        f"{status}",
        "⚖️",
        color
    )

with col3:
    metric_card(
        "Workouts",
        f"{workout.get('count', 0)}",
        f"Burn: {workout.get('calories', 0):.0f} kcal",
        "💪",
        "#00d9ff"
    )

with col4:
    streak = gamification.get("streak_workout", 0)
    metric_card(
        "Streak",
        f"{streak} days",
        "Keep it up! 🔥",
        "🔥",
        "#f59e0b"
    )

st.divider()

# ============ Calorie Equation Section ============
st.subheader("🔥 Daily Energy Balance")
st.caption("Maintenance + Activities + Workouts - Food = Net Balance")

sum_container = st.container()
with sum_container:
    # Prepare Waterfall Data
    bmr = summary.get("bmr", 2000)
    act_burn = summary.get("calories_burned_activity", 0) # Manual + Steps
    # Ensure workout burn is consistent
    work_burn = workout.get('calories', 0) 
    
    intake = summary.get("calories_intake", 0)
    if intake == 0 and nutrition.get('calories', 0) > 0:
        intake = nutrition.get('calories', 0)
    
    # Recalculate net based on freshest components
    net_bal = bmr + act_burn + work_burn - intake
    
    fig = go.Figure(go.Waterfall(
        name = "Energy Balance",
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "total"],
        x = ["BMR", "Activity + Steps", "Workout", "Food Intake", "Net Balance"],
        textposition = "outside",
        text = [f"{bmr:.0f}", f"+{act_burn:.0f}", f"+{work_burn:.0f}", f"-{intake:.0f}", f"{net_bal:.0f}"],
        y = [bmr, act_burn, work_burn, -intake, 0],
        connector = {"line":{"color":"rgba(63, 63, 63, 0.5)"}},
        decreasing = {"marker":{"color":"#ef4444"}}, 
        increasing = {"marker":{"color":"#10b981"}}, 
        totals = {"marker":{"color":"#3b82f6"}}
    ))
    
    fig.update_layout(
        title="",
        showlegend=False,
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(title="Calories (kcal)"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff") 
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Sleek Metrics Row below chart
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("BMR", f"{bmr:.0f}", help="Base Metabolic Rate (Mifflin-St Jeor)")
    sc2.metric("Activity Burn", f"{act_burn:.0f}", help="Steps and Cardio")
    sc3.metric("Workout Burn", f"{work_burn:.0f}", help="Strength Training")
    sc4.metric("Food Intake", f"{intake:.0f}", help="Logged Meals")


st.divider()

# Main content grid
col_left, col_right = st.columns([2, 1])

with col_left:
    section_header("Today's Overview", "Your progress at a glance")

    # Nutrition breakdown
    st.subheader("🍽️ Nutrition")
    nutri_col1, nutri_col2, nutri_col3, nutri_col4 = st.columns(4)

    with nutri_col1:
        stat_box("Protein", f"{nutrition.get('protein_g', 0):.0f}g", f"/ {150}g")
    with nutri_col2:
        stat_box("Carbs", f"{nutrition.get('carbs_g', 0):.0f}g", f"/ {250}g")
    with nutri_col3:
        stat_box("Fat", f"{nutrition.get('fat_g', 0):.0f}g", f"/ {73}g")
    with nutri_col4:
        # Real Water Data
        stat_box("Water", f"{water_ml / 1000:.1f}L", "/ 2.5L") # Assuming 2.5L target

    st.divider()

    # Activity
    st.subheader("🚴 Activity")
    activity_col1, activity_col2, activity_col3 = st.columns(3)

    with activity_col1:
        stat_box("Duration", f"{activities.get('total_duration_minutes', 0)} min", "total")
    with activity_col2:
        stat_box("Distance", f"{activities.get('total_distance_km', 0):.1f} km", "today")
    with activity_col3:
        stat_box("Calories", f"{activities.get('total_calories', 0):.0f}", "burned")

with col_right:
    section_header("XP & Levels", "Your progress")

    xp = gamification.get("xp", 0)
    level = gamification.get("level", 1)
    next_level_xp = gamification.get("next_level_xp", 1000)
    progress = (xp % 1000) / 1000 * 100

    st.metric("Current Level", level)
    st.markdown(f"**XP**: {xp % 1000:.0f} / {next_level_xp % 1000:.0f}")

    # Progress bar
    st.progress(min(progress / 100, 1.0))

    st.divider()

    st.subheader("Recent Badges")
    st.info("🏆 Earned: Consistent Warrior\n⭐ Level 5 Achieved\n💪 100 Push-ups")

st.divider()

# AI Coach quick tip
st.subheader("🤖 AI Coach Tip")
col_tip1, col_tip2 = st.columns([3, 1])

with col_tip1:
    try:
        tip_resp = requests.get(
            f"{get_api_base()}/ai-coach/tip",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if tip_resp.status_code == 200:
            tip = tip_resp.json().get("tip", "Keep pushing towards your goals!")
            st.info(f"🤖 **EpochOne AI**: {tip}")
        else:
            st.info("💡 **Coach Tip**: Keep up the great work and stay consistent!")
    except:
        st.info("💡 **Coach Tip**: Remember to log your meals for accurate tracking.")

with col_tip2:
    if st.button("Chat with Coach"):
        st.switch_page("pages/08_🤖_AI_Coach.py")

render_sidebar_footer()
