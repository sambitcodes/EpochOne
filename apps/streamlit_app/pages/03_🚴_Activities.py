"""Activity logging (cardio, sports, etc.)."""
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Activities", page_icon="🚴", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🚴 Activities")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

tab1, tab2, tab3 = st.tabs(["Log Activity", "History", "Integrations"])

with tab1:
    st.subheader("Log Manual Activity")

    with st.form("activity_form"):
        col1, col2 = st.columns(2)

        with col1:
            activity_type = st.selectbox(
                "Activity Type",
                ["Running", "Cycling", "Walking", "Swimming", "Sports", "Other"]
            )

        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, value=30)

        col3, col4 = st.columns(2)

        with col3:
            distance = st.number_input("Distance (km)", min_value=0.0, value=5.0)

        with col4:
            intensity = st.selectbox("Intensity", ["Easy", "Moderate", "Hard", "Extreme"])

        notes = st.text_area("Notes", placeholder="How was it?")

        if st.form_submit_button("✅ Log Activity"):
            payload = {
                "activity_type": activity_type.lower(),
                "duration_minutes": duration,
                "distance_km": distance,
                "intensity": intensity.lower(),
                "notes": notes
            }

            try:
                response = requests.post(
                    f"{get_api_base()}/activities/log",
                    json=payload,
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )

                if response.status_code == 200:
                    st.success("✅ Activity logged!")
                    st.balloons()
                else:
                    st.error(f"Failed: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Activity History")

    days = st.slider("Last N days", 1, 90, 7)

    try:
        response = requests.get(
            f"{get_api_base()}/activities/history?days={days}",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            activities = response.json()

            if activities:
                for activity in activities:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.write(f"**{activity.get('type', 'Activity').title()}**")
                        st.caption(activity.get('date', '')[:10])

                    with col2:
                        st.metric("Duration", f"{activity.get('duration_minutes', 0)} min")

                    with col3:
                        st.metric("Distance", f"{activity.get('distance_km', 0):.1f} km")

                    with col4:
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.metric("Cals (AI)", f"{(activity.get('calories') or 0):.0f}")
                        with c2:
                            if st.button("🗑️", key=f"del_{activity.get('id')}", help="Delete"):
                                try:
                                    res = requests.delete(
                                        f"{get_api_base()}/activities/{activity.get('id')}",
                                        params={"user_id": st.session_state.user_id},
                                        headers=get_headers()
                                    )
                                    if res.status_code == 204:
                                        st.success("Deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed")
                                except Exception as e:
                                    st.error(f"Err: {e}")

                    st.divider()
            else:
                st.info("No activities logged yet.")

    except Exception as e:
        st.error(f"Failed to load activities: {e}")

with tab3:
    st.subheader("Sync with Wearables")

    st.info("🔌 Connect your wearable devices to automatically sync activities")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Google Fit")
        if st.button("Connect Google Fit"):
            st.info("Redirecting to Google authorization...")
            # TODO: Implement OAuth flow

    with col2:
        st.subheader("Apple Health")
        if st.button("Connect Apple Health"):
            st.info("Download iOS companion app from App Store")
            # TODO: Link to App Store

render_sidebar_footer()
