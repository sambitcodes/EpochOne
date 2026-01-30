"""Sleep, hydration, and recovery tracking."""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px
from utils import get_api_base

st.set_page_config(page_title="Recovery", page_icon="😴", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

st.title("😴 Recovery")
st.caption("Optimize your rest and recovery.")

# --- Helper Functions ---
def fetch_history(metric_type, days=30):
    try:
        resp = requests.get(
            f"{get_api_base()}/wellness/logs",
            params={"user_id": st.session_state.user_id, "metric_type": metric_type, "days": days},
            headers=get_headers()
        )
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def delete_log_entry(log_id):
    try:
        requests.delete(
            f"{get_api_base()}/wellness/logs/{log_id}",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
    except:
        pass

def get_ai_insight(metric_type):
    try:
        resp = requests.get(
            f"{get_api_base()}/wellness/analysis",
            params={"user_id": st.session_state.user_id, "metric_type": metric_type},
            headers=get_headers()
        )
        if resp.status_code == 200:
            return resp.json().get("tip")
    except:
        pass
    return None

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Sleep", "Hydration", "Mood"])

# ================= SLEEP =================
with tab1:
    insight = get_ai_insight("sleep")
    if insight: st.info(f"💡 **AI Coach**: {insight}")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Log Sleep")
        with st.form("sleep_form"):
            date_val = st.date_input("Date", value=datetime.now())
            hours = st.number_input("Hours Slept", 0.0, 24.0, 7.5, 0.5)
            quality = st.slider("Quality (1-10)", 1, 10, 7)
            notes = st.text_area("Notes")
            
            if st.form_submit_button("✅ Save Sleep"):
                payload = {
                    "metric_type": "sleep",
                    "value_primary": hours,
                    "value_secondary": quality,
                    "notes": notes,
                    "date": date_val.strftime("%Y-%m-%dT%H:%M:%S")
                }
                requests.post(f"{get_api_base()}/wellness/logs", json=payload, params={"user_id": st.session_state.user_id}, headers=get_headers())
                st.success("Saved!")
                st.rerun()

    with c2:
        st.subheader("Sleep Trends")
        logs = fetch_history("sleep")
        if logs:
            df = pd.DataFrame(logs)
            df['date'] = pd.to_datetime(df['date'])
            
            fig = px.bar(df, x='date', y='value_primary', color='value_secondary', title="Sleep Duration & Quality", labels={'value_primary': 'Hours', 'value_secondary': 'Quality'})
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("History"):
                for l in logs:
                    cc1, cc2, cc3 = st.columns([2, 2, 1])
                    cc1.write(f"**{l['date'][:10]}**")
                    cc2.write(f"{l['value_primary']}h (Qual: {int(l['value_secondary'])})")
                    if cc3.button("🗑️", key=f"del_sleep_{l['id']}"):
                        delete_log_entry(l['id'])
                        st.rerun()

# ================= HYDRATION =================
with tab2:
    st.subheader("Hydration Tracker")
    
    # Calculate today's total
    logs = fetch_history("hydration", days=1) # Get mostly recent, filter in DF or logic
    # Filter for today effectively in UI
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_total = 0
    today_logs = []
    
    all_logs = fetch_history("hydration", days=7)
    for l in all_logs:
        if l['date'].startswith(today_str):
            today_total += l['value_primary']
    
    target = 2500 # 2.5L default target
    progress = min(today_total / target, 1.0)
    
    c_main, c_hist = st.columns([2, 1])
    
    with c_main:
        st.metric("Today's Water", f"{int(today_total)} ml", f"Target: {target} ml")
        st.progress(progress)
        
        st.write("### Quick Add")
        col1, col2, col3, col4 = st.columns(4)
        
        def add_water(amount):
            payload = {
                "metric_type": "hydration",
                "value_primary": amount,
                "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
            requests.post(f"{get_api_base()}/wellness/logs", json=payload, params={"user_id": st.session_state.user_id}, headers=get_headers())
            st.toast(f"Added {amount}ml 💧")
            # st.rerun() # Toast is nice, but rerun needed to update progress bar immediately
            
        if col1.button("+ 250ml"): 
            add_water(250)
            st.rerun()
        if col2.button("+ 500ml"): 
            add_water(500)
            st.rerun()
        if col3.button("+ 750ml"): 
            add_water(750)
            st.rerun()
        if col4.button("+ 1L"): 
            add_water(1000)
            st.rerun()

    with c_hist:
        st.write("**Recent Sips**")
        # Show today's logs
        logs_today = [l for l in all_logs if l['date'].startswith(today_str)]
        for l in logs_today:
            c1, c2 = st.columns([3, 1])
            c1.caption(f"{l['date'][11:16]} - {int(l['value_primary'])}ml")
            if c2.button("x", key=f"del_water_{l['id']}"):
                delete_log_entry(l['id'])
                st.rerun()

    st.divider()
    st.subheader("Weekly Hydration")
    if all_logs:
        df = pd.DataFrame(all_logs)
        df['date'] = pd.to_datetime(df['date']).dt.date
        daily = df.groupby('date')['value_primary'].sum().reset_index()
        fig = px.bar(daily, x='date', y='value_primary', title="Daily Water Intake (ml)")
        st.plotly_chart(fig, use_container_width=True)

# ================= MOOD =================
with tab3:
    insight = get_ai_insight("mood")
    if insight: st.info(f"💡 **AI Coach**: {insight}")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Log Mood")
        with st.form("mood_form"):
            date_val = st.date_input("Date", value=datetime.now())
            mood = st.slider("Mood (1-10)", 1, 10, 7, help="1=Awful, 10=Amazing")
            energy = st.slider("Energy (1-10)", 1, 10, 7)
            stress = st.slider("Stress (1-10)", 1, 10, 5)
            notes = st.text_area("Notes")
            
            if st.form_submit_button("✅ Save Log"):
                payload = {
                    "metric_type": "mood",
                    "value_primary": mood,
                    "value_secondary": energy,
                    "notes": f"Stress: {stress}. {notes}",
                    "date": date_val.strftime("%Y-%m-%dT%H:%M:%S")
                }
                requests.post(f"{get_api_base()}/wellness/logs", json=payload, params={"user_id": st.session_state.user_id}, headers=get_headers())
                st.success("Saved!")
                st.rerun()

    with c2:
        st.subheader("Mood Trends")
        logs = fetch_history("mood")
        if logs:
            df = pd.DataFrame(logs)
            df['date'] = pd.to_datetime(df['date'])
            
            fig = px.line(df, x='date', y=['value_primary', 'value_secondary'], markers=True, title="Mood vs Energy", labels={'value_primary': 'Mood', 'value_secondary': 'Energy'})
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Journal"):
                for l in logs:
                    st.markdown(f"**{l['date'][:10]}** | Mood: {l['value_primary']} | Energy: {l['value_secondary']}")
                    st.caption(l['notes'] or "")
                    if st.button("Delete Entry", key=f"del_mood_{l['id']}"):
                        delete_log_entry(l['id'])
                        st.rerun()
                    st.divider()

render_sidebar_footer()
