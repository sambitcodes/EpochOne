"""Workout logging and tracking page."""
import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Workouts", page_icon="🏋️", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🏋️ Workouts")

from utils import get_api_base
from utils.exercise_db import EXERCISE_DB, FAMOUS_SPLITS, EXERCISE_TYPES

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Tabs
tab1, tab2, tab3 = st.tabs(["Log Workout", "History", "Templates"])

# --- TAB 1: LOG WORKOUT ---
with tab1:
    st.subheader("Log New Workout")
    
    # Template Loader
    try:
        ts_resp = requests.get(f"{get_api_base()}/workouts/templates", params={"user_id": st.session_state.user_id}, headers=get_headers())
        user_templates = ts_resp.json() if ts_resp.status_code == 200 else []
    except: user_templates = []
    
    template_options = ["None"] + [t['name'] for t in user_templates]
    sel_template = st.selectbox("📂 Load Template", template_options)
    
    # Initialize or Load
    if 'log_exercises' not in st.session_state:
        st.session_state.log_exercises = [{"name": "", "sets": 3, "reps": 8, "weight": 0.0, "failure": False, "distance_km": 0.0, "duration_seconds": 0}]

    # Load Logic (Only if changed)
    if sel_template != "None":
        # Find template
        t_data = next((t for t in user_templates if t['name'] == sel_template), None)
        if t_data and st.session_state.get("last_loaded_template") != sel_template:
            try:
                loaded_exs = json.loads(t_data.get('exercises_json', '[]'))
                # Ensure failure key exists
                for ex in loaded_exs:
                    if 'failure' not in ex: ex['failure'] = False
                st.session_state.log_exercises = loaded_exs
                st.session_state.last_loaded_template = sel_template
                st.toast(f"Loaded '{sel_template}'!")
            except: pass

    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        with col1:
            # Date Input - Critical for "Analyze Day"
            workout_date = st.date_input("Date", value=datetime.now())
            duration = st.number_input("Duration (minutes)", min_value=0, value=60)
        with col2:
            workout_time = st.time_input("Time", value=datetime.now().time())
            # RPE removed as per new design

        notes = st.text_area("Workout Notes", placeholder="How did it go?")
        st.subheader("Exercises")
        
        def add_ex():
            st.session_state.log_exercises.append({"name": "", "sets": 3, "reps": 8, "weight": 0.0, "failure": False, "distance_km": 0.0, "duration_seconds": 0})
            
        # Build Exercise List
        all_exercises = []
        for v in EXERCISE_DB.values(): all_exercises.extend(v)
        all_exercises.sort()
        all_exercises.insert(0, "Custom")

        exercises_to_submit = []
        
        for i, ex in enumerate(st.session_state.log_exercises):
            st.markdown(f"**Exercise {i+1}**")
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            
            with c1:
                # Match existing name
                idx = 0
                if ex['name'] in all_exercises:
                    idx = all_exercises.index(ex['name'])
                
                sel_ex = st.selectbox(f"Exercise {i}", all_exercises, index=idx, key=f"ex_name_{i}")
                final_name = st.text_input("Name", value=ex['name'], key=f"ex_custom_{i}") if sel_ex == "Custom" else sel_ex
            
            # Determine type
            ex_type = EXERCISE_TYPES.get(final_name, "Strength")
            
            dist = 0.0
            dur_mins = 0
            
            with c2: 
                if ex_type == "Strength":
                    sets = st.number_input(f"Sets", 1, 99, ex.get('sets', 3), key=f"ex_sets_{i}")
                    # Reset cardio fields for strength
                    dist = 0.0
                else:
                    dist = st.number_input(f"Dist (km)", 0.0, 999.0, float(ex.get('distance_km', 0.0)), key=f"ex_dist_{i}")
                    sets = 1

            with c3: 
                if ex_type == "Strength":
                    reps = st.number_input(f"Reps", 1, 999, ex.get('reps', 8), key=f"ex_reps_{i}")
                    dur_mins = 0
                else:
                    dur_mins = st.number_input(f"Mins", 0, 999, int(ex.get('duration_seconds', 0)/60), key=f"ex_time_{i}")
                    reps = 1

            with c4: 
                if ex_type == "Strength":
                    weight = st.number_input(f"Kg", 0.0, 999.0, float(ex.get('weight', 0.0)), key=f"ex_weight_{i}")
                else:
                    st.write("---") # Placeholder
                    weight = 0.0

            with c5: 
                if ex_type == "Strength":
                    fail = st.checkbox("Failure?", value=ex.get('failure', False), key=f"ex_fail_{i}")
                else:
                    st.write("---")
                    fail = False
                
            exercises_to_submit.append({
                "name": final_name, 
                "sets": sets, 
                "reps": reps, 
                "weight": weight, 
                "failure": fail, 
                "distance_km": dist if ex_type == "Cardio" else None,
                "duration_seconds": (dur_mins * 60) if ex_type == "Cardio" else None, 
                "order": i
            })
            st.divider()

        b1, b2 = st.columns([1, 4])
        if b1.form_submit_button("➕ Add Exercise"):
            add_ex()
            st.rerun()
            
        if b2.form_submit_button("✅ Log Workout"):
            if any(e['name'] for e in exercises_to_submit):
                # Combine date and time
                full_dt = datetime.combine(workout_date, workout_time)
                
                payload = {
                    "duration_minutes": duration,
                    # "rpe": rpe, # Removed
                    "notes": notes,
                    "date": full_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "exercises": [e for e in exercises_to_submit if e['name']]
                }
                try:
                    requests.post(f"{get_api_base()}/workouts/log", json=payload, params={"user_id": st.session_state.user_id}, headers=get_headers())
                    st.success("Logged!")
                    # Reset
                    st.session_state.log_exercises = [{"name": "", "sets": 3, "reps": 8, "weight": 0.0, "failure": False}]
                    st.session_state.last_loaded_template = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Add exercise name")

# --- TAB 2: HISTORY ---
with tab2:
    st.subheader("Workout History")
    
    # 1. AI Analysis
    with st.expander("🤖 Daily Analysis", expanded=True):
        d_col1, d_col2 = st.columns([1, 3])
        with d_col1:
            analysis_date = st.date_input("Select Date", value=datetime.now())
        with d_col2:
            if st.button("Generate Report"):
                try:
                    a_resp = requests.get(
                        f"{get_api_base()}/workouts/daily-analysis",
                        params={"user_id": st.session_state.user_id, "date_str": analysis_date.strftime("%Y-%m-%d")},
                        headers=get_headers()
                    )
                    if a_resp.status_code == 200:
                        st.info(a_resp.json().get('analysis'))
                    else:
                        st.warning("No data found for this date.")
                except Exception as e:
                    st.error(f"Analysis error: {e}")

    st.divider()
    
    # 2. History List & Charts
    try:
        hist_resp = requests.get(f"{get_api_base()}/workouts/history", params={"user_id": st.session_state.user_id, "days": 30}, headers=get_headers())
        if hist_resp.status_code == 200:
            workouts = hist_resp.json()
            
            if workouts:
                # Visualization
                df = pd.DataFrame(workouts)
                df['date'] = pd.to_datetime(df['date'])
                
                # Chart 1: Duration/Calories
                st.subheader("Trends")
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    fig = px.bar(df, x='date', y='duration_minutes', title="Duration (mins)")
                    st.plotly_chart(fig, use_container_width=True)
                
                with c_chart2:
                    # Calories Trend
                    fig2 = px.bar(df, x='date', y='calories_burned', title="Calories Burned", color_discrete_sequence=['#FF5F1F'])
                    st.plotly_chart(fig2, use_container_width=True)

                st.divider()
                st.subheader("Log")
                prev_date = None
                for w in workouts:
                    w_date = w['date'][:10]
                    if w_date != prev_date:
                        st.markdown(f"#### {w_date}")
                        prev_date = w_date
                        
                    with st.expander(f"{w['exercise_count']} Exercises | {w['duration_minutes']} min | {int(w['calories_burned'] or 0)} kcal"):
                        c1, c2 = st.columns([4, 1])
                        if w.get('rpe'):
                             c1.write(f"RPE: {w['rpe']}/10")
                        if c2.button("🗑️", key=f"del_{w['id']}"):
                             requests.delete(f"{get_api_base()}/workouts/{w['id']}", params={"user_id": st.session_state.user_id}, headers=get_headers())
                             st.rerun()
            else:
                st.info("No history yet.")
    except:
        pass

# --- TAB 3: TEMPLATES ---
with tab3:
    st.subheader("Templates & Splits")
    
    st.info("💡 Tip: Created templates will appear in the 'Log Workout' tab dropdown.")
    
    # 1. Famous Splits
    split_choice = st.selectbox("Choose a Famous Split", ["Custom"] + list(FAMOUS_SPLITS.keys()))
    
    with st.expander("🛠️ Create New Template", expanded=True):
        t_name = st.text_input("Template Name", value=split_choice if split_choice != "Custom" else "")
        t_desc = st.text_input("Description", value=f"{split_choice} Routine")
        
        if 'temp_builder' not in st.session_state: st.session_state.temp_builder = []
            
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: cat = st.selectbox("Muscle Group", list(EXERCISE_DB.keys()))
        with c2: ex_choice = st.selectbox("Exercise", EXERCISE_DB[cat])
        with c3:
            if st.button("Add"):
                st.session_state.temp_builder.append({"name": ex_choice, "sets": 3, "reps": 8, "weight": 0, "failure": False})

        st.write("###### Exercises:")
        for i, ex in enumerate(st.session_state.temp_builder):
            cc1, cc2, cc3, cc4 = st.columns([3, 1, 1, 1])
            cc1.write(f"{i+1}. {ex['name']}")
            if cc4.button("x", key=f"rm_tmp_{i}"):
                st.session_state.temp_builder.pop(i)
                st.rerun()
                
        if st.button("💾 Save Template"):
            if t_name and st.session_state.temp_builder:
                payload = {
                    "name": t_name, "description": t_desc, "exercises": st.session_state.temp_builder
                }
                requests.post(f"{get_api_base()}/workouts/templates", json=payload, params={"user_id": st.session_state.user_id}, headers=get_headers())
                st.success("Template Saved!")
                st.session_state.temp_builder = []
                st.rerun()

render_sidebar_footer()
