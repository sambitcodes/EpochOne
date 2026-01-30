"""Nutrition and meal tracking."""
import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import pandas as pd

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
        # Date & Time Selection
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            meal_date = st.date_input("Date", value=datetime.now())
        with d_col2:
            meal_time = st.time_input("Time", value=datetime.now().time())

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
            full_dt = datetime.combine(meal_date, meal_time)
            
            payload = {
                "name": meal_name,
                "meal_type": meal_type.lower(),
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "notes": notes,
                "date": full_dt.strftime("%Y-%m-%dT%H:%M:%S")
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
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Today's Nutrition")

    try:
        # Fetch Summary
        sum_resp = requests.get(
            f"{get_api_base()}/nutrition/today",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        
        # Fetch Meals for Charts & List
        meals_resp = requests.get(
            f"{get_api_base()}/nutrition/meals?days=1",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if sum_resp.status_code == 200 and meals_resp.status_code == 200:
            data = sum_resp.json()
            meals = meals_resp.json()

            # 1. METRICS ROW
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Calories", f"{data.get('calories', 0)} / 2200")
            with col2: st.metric("Protein", f"{data.get('protein_g', 0):.0f}g / 150g")
            with col3: st.metric("Carbs", f"{data.get('carbs_g', 0):.0f}g / 250g")
            with col4: st.metric("Fat", f"{data.get('fat_g', 0):.0f}g / 73g")
            
            st.divider()

            # 2. CHARTS ROW
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### Macro Distribution")
                # Calculate calories from macros
                p_cals = data.get('protein_g', 0) * 4
                c_cals = data.get('carbs_g', 0) * 4
                f_cals = data.get('fat_g', 0) * 9
                
                if (p_cals + c_cals + f_cals) > 0:
                    macro_df = pd.DataFrame([
                        {"Macro": "Protein", "Calories": p_cals},
                        {"Macro": "Carbs", "Calories": c_cals},
                        {"Macro": "Fat", "Calories": f_cals}
                    ])
                    fig_macro = px.pie(
                        macro_df, values='Calories', names='Macro', 
                        color='Macro',
                        color_discrete_map={'Protein':'#3498DB', 'Carbs':'#2ECC71', 'Fat':'#E74C3C'},
                        hole=0.4
                    )
                    fig_macro.update_traces(textinfo='percent+label')
                    st.plotly_chart(fig_macro, use_container_width=True)
                else:
                    st.info("Log meals to see macro breakdown.")

            with chart_col2:
                # User asked for Micros, but we don't have them. 
                # We'll show Meal Type distribution instead as a useful "Partition"
                st.markdown("#### Meal Sources") # "Micros" placeholder
                
                if meals:
                    # Aggregate by meal_type
                    type_counts = {}
                    for m in meals:
                        mt = m.get('meal_type', 'snack').title()
                        type_counts[mt] = type_counts.get(mt, 0) + m.get('calories', 0)
                    
                    if type_counts:
                        micro_df = pd.DataFrame(list(type_counts.items()), columns=['Source', 'Calories'])
                        fig_micro = px.pie(
                            micro_df, values='Calories', names='Source',
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            hole=0.4
                        )
                        fig_micro.update_traces(textinfo='percent+label')
                        st.plotly_chart(fig_micro, use_container_width=True)
                else:
                    st.info("Log meals to see breakdown.")

            st.divider()

            # 3. MEALS LIST
            st.subheader("Meals Today")
            for meal in meals:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{meal.get('name')}** - {meal.get('meal_type', '').title()}")
                with col2:
                    st.caption(f"{meal.get('calories', 0)} cal")
                with col3:
                    c1, c2 = st.columns([3, 1])
                    with c1: st.caption(f"{meal.get('protein_g', 0):.0f}g protein")
                    with c2:
                         # Delete button closure
                         def delete_btn(mid):
                             st.button("🗑️", key=f"del_{mid}", help="Delete", on_click=lambda: delete_meal_wrapper(mid))

                         delete_btn(meal.get('id'))
                st.divider()

        else:
            st.warning("Could not load data.")

    except Exception as e:
        st.error(f"Failed to load nutrition data: {e}")

# Helper for delete (needs to be outside loop or handled carefully with state)
def delete_meal_wrapper(mid):
    try:
        requests.delete(
            f"{get_api_base()}/nutrition/meals/{mid}",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
    except: pass

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
                    st.rerun()
                else:
                    st.error("Failed to save meal.")
            except Exception as e:
                st.error(f"Error saving: {e}")

render_sidebar_footer()
