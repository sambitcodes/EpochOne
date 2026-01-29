"""Nutrition and meal tracking."""
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Nutrition", page_icon="🍽️", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🍽️ Nutrition")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

tab1, tab2, tab3 = st.tabs(["Log Meal", "Daily Summary", "AI Meal Helper"])

with tab1:
    st.subheader("Log Meal")

    with st.form("meal_form"):
        col1, col2 = st.columns(2)

        with col1:
            meal_name = st.text_input("Meal Name", placeholder="Chicken Pasta")

        with col2:
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

        col3, col4, col5, col6 = st.columns(4)

        with col3:
            calories = st.number_input("Calories", min_value=0, value=500)

        with col4:
            protein = st.number_input("Protein (g)", min_value=0.0, value=30.0)

        with col5:
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=60.0)

        with col6:
            fat = st.number_input("Fat (g)", min_value=0.0, value=15.0)

        notes = st.text_area("Notes", placeholder="Optional notes")

        if st.form_submit_button("✅ Log Meal"):
            payload = {
                "name": meal_name,
                "meal_type": meal_type.lower(),
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "notes": notes
            }

            try:
                response = requests.post(
                    f"{get_api_base()}/nutrition/meals",
                    json=payload,
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )

                if response.status_code == 200:
                    st.success("✅ Meal logged!")
                else:
                    st.error(f"Failed: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Today's Nutrition")

    try:
        response = requests.get(
            f"{get_api_base()}/nutrition/today",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Calories", f"{data.get('calories', 0)} / 2200")

            with col2:
                st.metric("Protein", f"{data.get('protein_g', 0):.0f}g / 150g")

            with col3:
                st.metric("Carbs", f"{data.get('carbs_g', 0):.0f}g / 250g")

            with col4:
                st.metric("Fat", f"{data.get('fat_g', 0):.0f}g / 73g")

            st.divider()

            st.subheader("Meals Today")

            try:
                meals_resp = requests.get(
                    f"{get_api_base()}/nutrition/meals?days=1",
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )

                if meals_resp.status_code == 200:
                    meals = meals_resp.json()

                    for meal in meals:
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.write(f"**{meal.get('name')}** - {meal.get('meal_type', '').title()}")

                        with col2:
                            st.caption(f"{meal.get('calories', 0)} cal")

                        with col3:
                            st.caption(f"{meal.get('protein_g', 0):.0f}g protein")

                        st.divider()

            except Exception as e:
                st.error(f"Failed to load meals: {e}")

    except Exception as e:
        st.error(f"Failed to load nutrition data: {e}")

with tab3:
    st.subheader("🤖 AI Meal Estimator")

    st.info("Describe your meal and AI will estimate macros!")

    meal_description = st.text_area(
        "Describe your meal",
        placeholder="e.g., A bowl of rice with grilled chicken and broccoli"
    )

    if st.button("🔮 Estimate Macros"):
        if not meal_description:
            st.warning("Please describe your meal first!")
        else:
            with st.spinner("AI is analyzing your meal..."):
                try:
                    response = requests.post(
                        f"{get_api_base()}/nutrition/estimate",
                        json={"description": meal_description},
                        headers=get_headers()
                    )
                    
                    if response.status_code == 200:
                        est = response.json()
                        st.session_state.current_estimation = est
                        
                        st.markdown(f"### 🥗 {est['name']}")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Calories", est['calories'])
                        col2.metric("Protein", f"{est['protein_g']}g")
                        col3.metric("Carbs", f"{est['carbs_g']}g")
                        col4.metric("Fat", f"{est['fat_g']}g")
                    else:
                        st.error("Failed to get estimation from AI.")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "current_estimation" in st.session_state:
        if st.button("💾 Save to Meal Log"):
            est = st.session_state.current_estimation
            payload = {
                "name": est['name'],
                "meal_type": "snack", # Default
                "calories": est['calories'],
                "protein_g": est['protein_g'],
                "carbs_g": est['carbs_g'],
                "fat_g": est['fat_g'],
                "notes": f"Estimated from: {meal_description}"
            }
            try:
                save_resp = requests.post(
                    f"{get_api_base()}/nutrition/meals",
                    json=payload,
                    params={"user_id": st.session_state.user_id},
                    headers=get_headers()
                )
                if save_resp.status_code == 200:
                    st.success("✅ Meal saved to today's log!")
                    del st.session_state.current_estimation
                else:
                    st.error("Failed to save meal.")
            except Exception as e:
                st.error(f"Error saving: {e}")

render_sidebar_footer()
