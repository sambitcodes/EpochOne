"""Body metrics and progress tracking."""
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Body Metrics", page_icon="⚖️", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("⚖️ Body Metrics")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

tab1, tab2, tab3 = st.tabs(["Log Metric", "Progress", "Photos"])

with tab1:
    st.subheader("Log Body Metric")

    with st.form("metric_form"):
        col1, col2 = st.columns(2)

        with col1:
            metric_type = st.selectbox(
                "Metric Type",
                ["Weight", "Chest", "Waist", "Biceps", "Thighs", "Body Fat %"]
            )

        with col2:
            metric_value = st.number_input("Value", min_value=0.0, value=75.0)

        col3, col4 = st.columns(2)

        with col3:
            unit = st.selectbox("Unit", ["kg", "lbs", "cm", "in", "%"])

        with col4:
            st.write("") # spacing

        notes = st.text_area("Notes", placeholder="Optional")

        if st.form_submit_button("✅ Log Metric"):
            payload = {
                "metric_type": metric_type.lower(),
                "value": metric_value,
                "unit": unit,
                "notes": notes
            }

            try:
                response = requests.post(
                    f"{get_api_base()}/metrics/",
                    json=payload,
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )

                if response.status_code == 200:
                    st.success("✅ Metric logged!")
                else:
                    st.error(f"Failed: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Progress Charts")

    try:
        response = requests.get(
            f"{get_api_base()}/metrics/latest",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            latest = response.json()

            col1, col2, col3 = st.columns(3)

            with col1:
                if "weight" in latest:
                    w = latest["weight"]
                    st.metric("Current Weight", f"{w['value']}{w['unit']}")

            with col2:
                if "waist" in latest:
                    w = latest["waist"]
                    st.metric("Waist", f"{w['value']}{w['unit']}")

            with col3:
                if "chest" in latest:
                    c = latest["chest"]
                    st.metric("Chest", f"{c['value']}{c['unit']}")

            st.divider()

            # Progress chart
            st.subheader("Weight Trend (90 days)")

            try:
                history_resp = requests.get(
                    f"{get_api_base()}/metrics/history?metric_type=weight&days=90",
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )

                if history_resp.status_code == 200:
                    history = history_resp.json()

                    if history:
                        dates = [m['date'][:10] for m in history]
                        values = [m['value'] for m in history]

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates, y=values,
                            mode='lines+markers',
                            name='Weight',
                            line=dict(color='#00d9ff', width=2),
                            marker=dict(size=6)
                        ))

                        fig.update_layout(
                            hovermode='x unified',
                            plot_bgcolor='#1a1f2e',
                            paper_bgcolor='#0f1419',
                            font=dict(color='#f1f5f9'),
                            xaxis=dict(gridcolor='#334155'),
                            yaxis=dict(gridcolor='#334155')
                        )

                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Failed to load history: {e}")

    except Exception as e:
        st.error(f"Failed to load metrics: {e}")

with tab3:
    st.subheader("Progress Photos")

    col1, col2 = st.columns(2)

    with col1:
        angle = st.selectbox("Angle", ["Front", "Back", "Side Left", "Side Right"])

    with col2:
        uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        st.image(uploaded_file, caption=f"{angle} view")

        if st.button("Save Photo"):
            st.info("✅ Photo saved! (S3 upload coming soon)")

    st.divider()

    st.subheader("Photo Timeline")
    st.info("📸 Your progress photos will appear here")

render_sidebar_footer()
