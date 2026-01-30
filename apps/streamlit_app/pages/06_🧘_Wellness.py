"""Wellness tracking and AI insights."""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Wellness", page_icon="🧘", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

st.title("🧘 Wellness")
st.caption("Track your vital health metrics.")

# Tabs for different metrics
tab_labels = [
    "HRV", "RHR", "VO2 Max", "Blood Pressure", 
    "Respiratory Rate", "SpO2", "Glucose"
]
tabs = st.tabs(tab_labels)

metric_map = {
    "HRV": "hrv",
    "RHR": "rhr",
    "VO2 Max": "vo2max",
    "Blood Pressure": "bp",
    "Respiratory Rate": "resp_rate",
    "SpO2": "spo2",
    "Glucose": "glucose"
}

def render_tab_content(tab_name, metric_key):
    """Render content for a wellness tab."""
    
    # 1. AI Insight Section
    # Check for recent data to display AI tip
    try:
        tip_resp = requests.get(
            f"{get_api_base()}/wellness/analysis",
            params={"user_id": st.session_state.user_id, "metric_type": metric_key},
            headers=get_headers()
        )
        if tip_resp.status_code == 200:
            msg = tip_resp.json().get("tip")
            st.info(f"💡 **AI Insight**: {msg}")
    except:
        pass

    # 2. Main Layout
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Log Entry")
        with st.form(f"form_{metric_key}"):
            date_val = st.date_input("Date", value=datetime.now())
            
            val1 = 0.0
            val2 = 0.0
            
            if metric_key == "bp":
                c1, c2 = st.columns(2)
                with c1: val1 = st.number_input("Systolic (mmHg)", min_value=0.0, value=120.0)
                with c2: val2 = st.number_input("Diastolic (mmHg)", min_value=0.0, value=80.0)
            else:
                label_map = {
                    "hrv": "HRV (ms)",
                    "rhr": "Resting Heart Rate (bpm)",
                    "vo2max": "VO2 Max (ml/kg/min)",
                    "resp_rate": "Breaths per min",
                    "spo2": "SpO2 (%)",
                    "glucose": "Glucose (mg/dL)"
                }
                val1 = st.number_input(label_map.get(metric_key, "Value"), min_value=0.0, value=0.0)

            notes = st.text_area("Notes", placeholder="Optional context")
            
            if st.form_submit_button("✅ Save Log"):
                payload = {
                    "metric_type": metric_key,
                    "value_primary": val1,
                    "value_secondary": val2 if metric_key == "bp" else None,
                    "notes": notes,
                    "date": date_val.strftime("%Y-%m-%dT%H:%M:%S")
                }
                try:
                    res = requests.post(
                        f"{get_api_base()}/wellness/logs",
                        json=payload,
                        params={"user_id": st.session_state.user_id},
                        headers=get_headers()
                    )
                    if res.status_code == 200:
                        st.success("Saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_right:
        st.subheader("Trends")
        
        # Fetch History
        try:
            hist_resp = requests.get(
                f"{get_api_base()}/wellness/logs",
                params={"user_id": st.session_state.user_id, "metric_type": metric_key, "days": 90},
                headers=get_headers()
            )
            
            if hist_resp.status_code == 200:
                logs = hist_resp.json()
                
                if logs:
                    df = pd.DataFrame(logs)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    # Chart
                    if metric_key == "bp":
                        fig = px.line(df, x='date', y=['value_primary', 'value_secondary'], markers=True, title=f"{tab_name} History")
                        fig.update_layout(yaxis_title="mmHg")
                    else:
                        fig = px.line(df, x='date', y='value_primary', markers=True, title=f"{tab_name} History")
                        
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # List with Delete
                    with st.expander("Message History", expanded=False):
                        for log in logs:
                            c1, c2, c3 = st.columns([2, 2, 1])
                            with c1:
                                st.caption(log['date'][:10])
                            with c2:
                                if metric_key == "bp":
                                    st.write(f"**{log['value_primary']:.0f}/{log['value_secondary']:.0f}**")
                                else:
                                    st.write(f"**{log['value_primary']:.1f}**")
                            with c3:
                                def delete_log(lid):
                                    try:
                                        requests.delete(f"{get_api_base()}/wellness/logs/{lid}", params={"user_id": st.session_state.user_id}, headers=get_headers())
                                    except: pass
                                    
                                st.button("🗑️", key=f"del_{log['id']}", on_click=delete_log, args=(log['id'],))
                else:
                    st.info("No data yet. Start logging!")
        except Exception as e:
            st.error(f"Error loading history: {e}")

# Render Tabs
for i, tab_label in enumerate(tab_labels):
    with tabs[i]:
        render_tab_content(tab_label, metric_map[tab_label])

render_sidebar_footer()
