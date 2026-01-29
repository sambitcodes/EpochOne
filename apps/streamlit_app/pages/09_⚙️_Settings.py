"""User settings and preferences."""
import streamlit as st
import requests

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer, logout_user
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("⚙️ Settings")

from utils import get_api_base, calculate_metrics, kg_to_lbs, lbs_to_kg, cm_to_in, in_to_cm, cm_to_ft_in, ft_in_to_cm

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Fetch profile at once for all tabs
if "user_profile" not in st.session_state or st.session_state.user_profile is None:
    try:
        response = requests.get(
            f"{get_api_base()}/users/profile",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if response.status_code == 200:
            st.session_state.user_profile = response.json()
    except Exception as e:
        st.error(f"Failed to load profile: {e}")

user = st.session_state.get("user_profile", {})

def update_profile(payload):
    """Helper to update profile and sync session state."""
    try:
        update_resp = requests.put(
            f"{get_api_base()}/users/profile",
            json=payload,
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if update_resp.status_code == 200:
            updated_user = update_resp.json()
            st.session_state.user_profile = updated_user
            return True, updated_user
        return False, update_resp.text
    except Exception as e:
        return False, str(e)

tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Preferences", "Goals", "Privacy"])

# Unit Controls OUTSIDE for global responsive effect
st.markdown("### 📏 Quick Unit Toggle")
ut_col1, ut_col2, ut_col3 = st.columns(3)
with ut_col1:
    use_lbs = st.toggle("Display Weight in lbs", value=user.get("units") == "imperial", key="set_use_lbs")
    w_unit = "lbs" if use_lbs else "kg"
with ut_col2:
    use_in = st.toggle("Display Measurements in inches", value=user.get("units") == "imperial", key="set_use_in")
    m_unit = "inches" if use_in else "cm"
with ut_col3:
    h_unit = st.selectbox("Height Display Unit", ["cm", "ft & in", "inches"], index=0 if user.get("units") == "metric" else 1, key="set_h_unit")

with tab1:
    st.subheader("Profile Info")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value=user.get("name", ""))
        age = st.number_input("Age", min_value=13, value=user.get("age") or 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["male", "female", "other"].index(user.get("gender") or "male"))
        
        curr_w = user.get("weight") or 70.0
        display_w = curr_w if not use_lbs else kg_to_lbs(curr_w)
        weight_val = st.number_input(f"Weight ({w_unit})", value=float(display_w))
    
    with col2:
        st.text_input("Email", value=user.get("email", ""), disabled=True)
        
        curr_h = user.get("height") or 170.0
        st.markdown(f"**Height ({h_unit})**")
        if h_unit == "cm":
            height_val = st.number_input("Height (cm)", value=float(curr_h), label_visibility="collapsed")
        elif h_unit == "ft & in":
            h_ft, h_in = cm_to_ft_in(curr_h)
            hf_col1, hf_col2 = st.columns(2)
            with hf_col1: s_h_ft = st.number_input("ft", min_value=1, max_value=8, value=int(h_ft))
            with hf_col2: s_h_in = st.number_input("in", min_value=0, max_value=11, value=int(h_in))
            height_val = (s_h_ft, s_h_in)
        else:
            height_val = st.number_input("Height (inches)", value=float(cm_to_in(curr_h)), label_visibility="collapsed")

        curr_tw = user.get("target_weight") or 65.0
        display_tw = curr_tw if not use_lbs else kg_to_lbs(curr_tw)
        target_weight_val = st.number_input(f"Target Weight ({w_unit})", value=float(display_tw))
        
        step_goal = st.number_input("Daily Step Goal", value=user.get("step_goal") or 10000)

    st.divider()
    st.subheader("Profile Picture")
    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    
    picture_b64 = user.get("picture")
    
    if uploaded_file is not None:
        import base64
        bytes_data = uploaded_file.getvalue()
        picture_b64 = f"data:image/{uploaded_file.type.split('/')[-1]};base64," + base64.b64encode(bytes_data).decode()
        st.image(bytes_data, width=100, caption="Preview")
    elif picture_b64:
        st.image(picture_b64, width=100, caption="Current Picture")

    if st.button("Save Profile Changes", type="primary"):
        w_kg = weight_val if not use_lbs else lbs_to_kg(weight_val)
        tw_kg = target_weight_val if not use_lbs else lbs_to_kg(target_weight_val)
        if h_unit == "cm": h_cm = height_val
        elif h_unit == "ft & in": h_cm = ft_in_to_cm(height_val[0], height_val[1])
        else: h_cm = in_to_cm(height_val)
        
        calc = calculate_metrics(w_kg, h_cm, age, gender.lower(), user.get("lifestyle_type") or "sedentary", user.get("waist") or 85, user.get("neck") or 40, user.get("hip"))
        success, msg = update_profile({
            "name": name, "age": age, "gender": gender.lower(),
            "weight": w_kg, "height": h_cm, "target_weight": tw_kg, "step_goal": step_goal,
            "units": "imperial" if (use_lbs or use_in) else "metric",
            "bmi": calc.get("bmi"), "body_fat_pct": calc.get("body_fat"),
            "lean_body_mass": calc.get("lbm"), "maintenance_calories": calc.get("maintenance"),
            "picture": picture_b64
        })
        if success: st.success("✅ Profile updated!"); st.rerun()
        else: st.error(f"Update failed: {msg}")

with tab2:
    st.subheader("Preferences")
    with st.form("pref_form"):
        units = st.selectbox("Global Preference", ["Metric (kg, cm)", "Imperial (lbs, in)"], index=0 if user.get("units") == "metric" else 1)
        ai_model = st.selectbox("Preferred AI Model", ["llama-3.3-70b-versatile", "groq/compound", "openai/gpt-oss-120b"], index=0)
        lifestyle = st.selectbox("Lifestyle Type", ["Sedentary", "Lightly Active", "Active", "Very Active"], 
                                index=["sedentary", "lightly_active", "active", "very_active"].index(user.get("lifestyle_type") or "sedentary"))
        if st.form_submit_button("Save Preferences"):
            success, msg = update_profile({
                "units": "metric" if units.startswith("Metric") else "imperial",
                "preferred_ai_model": ai_model,
                "lifestyle_type": lifestyle.lower().replace(" ", "_")
            })
            if success: st.success("✅ Preferences updated!"); st.rerun()
            else: st.error(f"Update failed: {msg}")

with tab3:
    st.subheader("Measurements & Goals")
    
    col1, col2 = st.columns(2)
    with col1:
        # LIVE CONVERSION for measurements
        curr_wa = user.get("waist") or 85.0
        display_wa = curr_wa if not use_in else cm_to_in(curr_wa)
        waist_val = st.number_input(f"Waist ({m_unit})", value=float(display_wa))
        
        curr_ne = user.get("neck") or 40.0
        display_ne = curr_ne if not use_in else cm_to_in(curr_ne)
        neck_val = st.number_input(f"Neck ({m_unit})", value=float(display_ne))

        curr_hi = user.get("hip") or 95.0
        display_hi = curr_hi if not use_in else cm_to_in(curr_hi)
        hip_val = st.number_input(f"Hip ({m_unit})", value=float(display_hi))
    
    with col2:
        curr_ch = user.get("chest") or 100.0
        display_ch = curr_ch if not use_in else cm_to_in(curr_ch)
        chest_val = st.number_input(f"Chest ({m_unit})", value=float(display_ch))

        curr_th = user.get("thigh") or 55.0
        display_th = curr_th if not use_in else cm_to_in(curr_th)
        thigh_val = st.number_input(f"Thigh ({m_unit})", value=float(display_th))

    st.divider()
    calorie_target = st.number_input("Daily Calorie Target", min_value=1200, value=user.get("calorie_target", 2200))
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1: protein = st.number_input("Protein (g)", min_value=50, value=user.get("protein_target", 150))
    with m_col2: carbs = st.number_input("Carbs (g)", min_value=100, value=user.get("carb_target", 250))
    with m_col3: fat = st.number_input("Fat (g)", min_value=40, value=user.get("fat_target", 73))

    st.divider()
    m_val = user.get("motive") or "general_health"
    current_motive = m_val.replace("_", " ").title()
    motive_options = ["Weight Loss", "Muscle Gain", "Endurance", "General Health"]
    motive = st.selectbox("Goal", motive_options, index=motive_options.index(current_motive) if current_motive in motive_options else 0)
    workout_days = st.slider("Workout Days", 1, 7, value=user.get("workout_days_per_week") or 3)

    if st.button("Save Goals & Measurements", type="primary"):
        # Convert back to metric for storage
        wa_cm = waist_val if not use_in else in_to_cm(waist_val)
        ne_cm = neck_val if not use_in else in_to_cm(neck_val)
        hi_cm = hip_val if not use_in else in_to_cm(hip_val)
        ch_cm = chest_val if not use_in else in_to_cm(chest_val)
        th_cm = thigh_val if not use_in else in_to_cm(thigh_val)

        calc = calculate_metrics(user.get("weight") or 70.0, user.get("height") or 170.0, user.get("age") or 25, user.get("gender") or "male", user.get("lifestyle_type") or "sedentary", wa_cm, ne_cm, hi_cm)
        success, msg = update_profile({
            "waist": wa_cm, "neck": ne_cm, "hip": hi_cm, "chest": ch_cm, "thigh": th_cm,
            "calorie_target": calorie_target, "protein_target": protein, "carb_target": carbs, "fat_target": fat,
            "motive": motive.lower().replace(" ", "_"), "workout_days_per_week": workout_days,
            "bmi": calc.get("bmi"), "body_fat_pct": calc.get("body_fat"), "lean_body_mass": calc.get("lbm"), "maintenance_calories": calc.get("maintenance")
        })
        if success: st.success("✅ Saved!"); st.rerun()
        else: st.error(f"Failed: {msg}")

with tab4:
    st.subheader("Privacy & Data")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Share profile publicly", value=False)
        st.checkbox("Allow AI Coach to analyze data", value=True)

    with col2:
        st.checkbox("Share progress with friends", value=False)
        st.checkbox("Opt-in to product improvements", value=True)

    st.divider()

    st.subheader("Account Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Data (CSV)"):
            st.info("📥 Data export initiated")

    with col2:
        st.error("🗑️ Danger Zone")
        if st.button("Delete My Account", type="secondary"):
            st.session_state.confirm_delete = True

        if st.session_state.get("confirm_delete", False):
            st.warning("⚠️ This action is PERMANENT. All your workouts, meals, and profile data will be deleted.")
            confirmed = st.checkbox("I understand and want to delete my account forever")
            if confirmed:
                if st.button("🔥 Confirm Permanent Deletion", type="primary"):
                    try:
                        del_resp = requests.delete(
                            f"{get_api_base()}/users/",
                            params={"user_id": st.session_state.user_id},
                            headers=get_headers()
                        )
                        if del_resp.status_code == 204:
                            st.success("Account deleted successfully.")
                            # Clear all session state
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            st.rerun()
                        else:
                            st.error(f"Deletion failed: {del_resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

render_sidebar_footer()
