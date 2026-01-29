"""Sleep, hydration, and recovery tracking."""
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Recovery", page_icon="😴", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("😴 Recovery & Wellness")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

tab1, tab2, tab3 = st.tabs(["Log Sleep", "Hydration", "Mood"])

with tab1:
    st.subheader("Sleep Tracking")

    with st.form("sleep_form"):
        col1, col2 = st.columns(2)

        with col1:
            sleep_hours = st.number_input("Hours Slept", min_value=0.0, max_value=12.0, value=8.0, step=0.5)

        with col2:
            sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)

        notes = st.text_area("Notes", placeholder="How was your sleep?")

        if st.form_submit_button("✅ Log Sleep"):
            st.success(f"✅ Logged {sleep_hours} hours of sleep!")

with tab2:
    st.subheader("Hydration")

    st.info("💧 Target: 2L per day (8 cups)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("+ 250ml"):
            st.success("Added 250ml")

    with col2:
        if st.button("+ 500ml"):
            st.success("Added 500ml")

    with col3:
        if st.button("+ 750ml"):
            st.success("Added 750ml")

    with col4:
        if st.button("+ 1L"):
            st.success("Added 1L")

    st.divider()

    st.metric("Today's Water", "1.2L / 2L")
    st.progress(1.2 / 2)

with tab3:
    st.subheader("Mood & Energy")

    with st.form("mood_form"):
        col1, col2 = st.columns(2)

        with col1:
            energy = st.slider("Energy Level (1-10)", 1, 10, 7)

        with col2:
            mood = st.slider("Mood (1-10)", 1, 10, 7)

        stress = st.slider("Stress Level (1-10)", 1, 10, 5)

        notes = st.text_area("How are you feeling?", placeholder="Optional notes")

        if st.form_submit_button("✅ Log Mood"):
            st.success("✅ Mood logged!")

render_sidebar_footer()
