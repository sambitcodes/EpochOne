"""Workout logging and tracking page."""
import streamlit as st
import requests
from datetime import datetime
import json

st.set_page_config(page_title="Workouts", page_icon="🏋️", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🏋️ Workouts")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Tabs
tab1, tab2, tab3 = st.tabs(["Log Workout", "History", "Templates"])

with tab1:
    st.subheader("Log New Workout")

    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=0, value=60)
            
        with col2:
            rpe = st.slider("Rate of Perceived Exertion (1-10)", 1, 10, 7)

        notes = st.text_area("Workout Notes", placeholder="How did it go?")

        st.subheader("Exercises")

        num_exercises = st.number_input("Number of exercises", min_value=0, max_value=10, value=1)

        exercises = []
        for i in range(num_exercises):
            st.write(f"**Exercise {i+1}**")
            ex_col1, ex_col2, ex_col3 = st.columns(3)

            with ex_col1:
                ex_name = st.text_input(f"Exercise name {i}", placeholder="Bench Press")

            with ex_col2:
                ex_sets = st.number_input(f"Sets {i}", min_value=1, value=3, key=f"sets_{i}")

            with ex_col3:
                ex_reps = st.number_input(f"Reps {i}", min_value=1, value=8, key=f"reps_{i}")

            ex_weight = st.number_input(f"Weight (kg) {i}", min_value=0.0, value=0.0, key=f"weight_{i}")

            if ex_name:
                exercises.append({
                    "name": ex_name,
                    "sets": ex_sets,
                    "reps": ex_reps,
                    "weight": ex_weight,
                    "rest_seconds": 60,
                    "notes": None,
                    "order": i
                })

            st.divider()

        if st.form_submit_button("✅ Log Workout"):
            if exercises:
                payload = {
                    "duration_minutes": duration,
                    "rpe": rpe,
                    # "calories_burned": calories, # Let AI handle it
                    "notes": notes,
                    "exercises": exercises
                }

                try:
                    response = requests.post(
                        f"{get_api_base()}/workouts/log",
                        json=payload,
                        params={"user_id": st.session_state.user_id},
                        headers=get_headers()
                    )

                    if response.status_code == 200:
                        st.success("✅ Workout logged successfully!")
                        st.balloons()
                    else:
                        st.error(f"Failed: {response.text}")

                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please add at least one exercise")

with tab2:
    st.subheader("Workout History")

    days = st.slider("Last N days", 1, 90, 30)

    try:
        response = requests.get(
            f"{get_api_base()}/workouts/history?days={days}",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            workouts = response.json()

            if workouts:
                for workout in workouts:
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.write(f"**{workout.get('date', 'N/A')[:10]}**")
                        st.caption(f"{workout.get('exercise_count', 0)} exercises • {workout.get('duration_minutes', 0)} min")

                    with col2:
                        cols_hist1, cols_hist2 = st.columns(2)
                        with cols_hist1:
                            if workout.get('rpe'):
                                st.metric("RPE", workout['rpe'])
                        with cols_hist2:
                            if workout.get('calories_burned'):
                                st.metric("Cals", f"{(workout.get('calories_burned') or 0):.0f}")
                            
                    with col3:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.button("View", key=workout.get('id'))
                        with c2:
                            if st.button("🗑️", key=f"del_{workout.get('id')}", help="Delete workout"):
                                try:
                                    res = requests.delete(
                                        f"{get_api_base()}/workouts/{workout.get('id')}",
                                        params={"user_id": st.session_state.user_id},
                                        headers=get_headers()
                                    )
                                    if res.status_code == 204:
                                        st.success("Deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete")
                                except Exception as e:
                                    st.error(f"Error: {e}")

                    st.divider()
            else:
                st.info("No workouts logged yet. Start with a new workout!")

    except Exception as e:
        st.error(f"Failed to load history: {e}")

with tab3:
    st.subheader("Workout Templates")

    try:
        response = requests.get(
            f"{get_api_base()}/workouts/templates",
            headers=get_headers()
        )

        if response.status_code == 200:
            templates = response.json()

            for template in templates:
                with st.expander(f"📋 {template.get('name')}"):
                    st.write(template.get('description', 'No description'))

                    if st.button("Use Template", key=f"use_{template.get('id')}"):
                        st.info("Template loaded! Use the form above to start.")

            st.divider()

            with st.expander("➕ Create New Template"):
                with st.form("template_form"):
                    template_name = st.text_input("Template Name")
                    template_desc = st.text_area("Description")

                    if st.form_submit_button("Save Template"):
                        st.success("Template saved!")

    except Exception as e:
        st.error(f"Failed to load templates: {e}")

render_sidebar_footer()
