import streamlit as st
import requests
import time
from datetime import datetime
import logging

# Setup page config first (must be before any other st calls)
st.set_page_config(
    page_title="EpochOne",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import shared styles
from ui.styles import apply_theme
apply_theme()

logger = logging.getLogger(__name__)

# ============ Auth Check ============
def init_session_state():
    """Initialize session state for auth and UI."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
        st.session_state.user = None
        st.session_state.user_id = None

    # Handle Fitbit Callback (Redirects to Home)
    qp = st.query_params
    if "code" in qp and "state" in qp:
        try:
            # We don't have access_token if session reset, but we have user_id in state
            # The backend callback doesn't strictly require a bearer token if we pass user_id in body/state
            # But our current API router might enforce dependency?
            # Let's check router. NO, fitbit_callback endpoint depends on get_db but not get_current_user/auth
            
            from utils import get_api_base
            code = qp["code"]
            state = qp["state"]
            
            resp = requests.post(
                f"{get_api_base()}/integrations/fitbit/callback",
                json={"code": code, "state": state}
            )
            
            if resp.status_code == 200:
                st.toast("✅ Fitbit connected successfully! Please log in again if needed.")
                st.query_params.clear()
            else:
                st.error(f"Fitbit connection failed: {resp.text}")
        except Exception as e:
            st.error(f"Callback error: {e}")

init_session_state()

from utils import get_api_base
from streamlit_oauth import OAuth2Component
import os

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"

def is_authenticated():
    """Check if user is logged in."""
    return st.session_state.get("access_token") is not None

def login_user():
    """Login/SignUp view."""
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 2rem; font-size: 3.5rem;'>🏋️
            <span style='color: #FF69B4;'>Epoch</span><span style='color: #39FF14;'>One</span>
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #DCA06D; margin-bottom: 2rem;'>Track your workouts, nutrition, and get AI-powered coaching.</p>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab_login:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("💡 Manual Login")
            with st.form("manual_login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        try:
                            api_url = get_api_base()
                            response = requests.post(
                                f"{api_url}/auth/login",
                                json={"username": username, "password": password}
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.access_token = data["access_token"]
                                st.session_state.user = data["user"]
                                st.session_state.user_id = data["user"]["id"]
                                
                                # Fetch full profile immediately
                                try:
                                    profile_resp = requests.get(
                                        f"{api_url}/users/profile",
                                        params={"user_id": st.session_state.user_id, "_t": str(time.time())},
                                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                                    )
                                    if profile_resp.status_code == 200:
                                        st.session_state.user_profile = profile_resp.json()
                                except:
                                    pass
                                
                                st.success("✅ Logged in!")
                                st.rerun()
                            else:
                                st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

        with col2:
            st.info("🌐 Social Login")
            if not AUTH0_DOMAIN or not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
                st.error("Auth0 configuration is missing in environment.")
            else:
                oauth2 = OAuth2Component(
                    AUTH0_CLIENT_ID,
                    AUTH0_CLIENT_SECRET,
                    AUTH0_AUTHORIZE_URL,
                    AUTH0_TOKEN_URL,
                    AUTH0_TOKEN_URL,
                    None
                )
                
                result = oauth2.authorize_button(
                    name="Connect with Google ",
                    redirect_uri="http://localhost:8501",
                    scope="openid email profile",
                    key="auth0_button",
                    use_container_width=True,
                )
                
                if result and "token" in result:
                    token = result.get("token")
                    id_token = token.get("id_token")
                    
                    try:
                        import jwt
                        user_info = jwt.decode(id_token, options={"verify_signature": False})
                        
                        api_url = get_api_base()
                        sync_resp = requests.post(
                            f"{api_url}/auth/auth0-callback",
                            params={
                                "auth0_sub": user_info.get("sub"),
                                "email": user_info.get("email"),
                                "name": user_info.get("name"),
                                "picture": user_info.get("picture")
                            }
                        )
                        
                        if sync_resp.status_code == 200:
                            sync_data = sync_resp.json()
                            st.session_state.access_token = token.get("access_token")
                            st.session_state.user = user_info
                            st.session_state.user_id = sync_data["user_id"]
                            st.success("✅ Logged in via Google")
                            st.rerun()
                        else:
                            st.error(f"Backend sync failed: {sync_resp.text}")
                    except Exception as e:
                        st.error(f"Auth processing error: {e}")

            if st.button("🚀 Login as Demo User (One-Click)", use_container_width=True):
                try:
                    with st.spinner("Logging in..."):
                        resp = requests.post(f"{get_api_base()}/auth/dev-login")
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.access_token = data["access_token"]
                            st.session_state.user = data["user"]
                            st.session_state.user_id = data["user"]["id"]
                            
                            # Fetch full profile immediately
                            try:
                                profile_resp = requests.get(
                                    f"{get_api_base()}/users/profile",
                                    params={"user_id": st.session_state.user_id, "_t": str(time.time())},
                                    headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                                )
                                if profile_resp.status_code == 200:
                                    st.session_state.user_profile = profile_resp.json()
                            except:
                                pass
                                
                            st.success("✅ Logged in as Demo User")
                            st.rerun()
                        else:
                            st.error(f"Dev login failed: {resp.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    with tab_signup:
        st.info("✨ Create a new account")
        with st.form("signup_form"):
            new_name = st.text_input("Full Name")
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
            with col2:
                new_email = st.text_input("Email")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            signup_submit = st.form_submit_button("Sign Up", use_container_width=True, type="primary")
            
            if signup_submit:
                if not new_name or not new_username or not new_email or not new_password:
                    st.error("All fields are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    try:
                        api_url = get_api_base()
                        signup_resp = requests.post(
                            f"{api_url}/auth/register",
                            json={
                                "name": new_name,
                                "username": new_username,
                                "email": new_email,
                                "password": new_password
                            }
                        )
                        if signup_resp.status_code == 200:
                            st.success("🎉 Account created! You can now log in.")
                            st.info("Switching to Login tab...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Sign up failed: {signup_resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

    with st.expander("Troubleshooting / Manual Access"):
        manual_token = st.text_input("Enter JWT Access Token", type="password")
        if st.button("Manual Token Login"):
            if manual_token:
                st.session_state.access_token = manual_token
                st.session_state.user = {"sub": "manual_user", "email": "manual@example.com"}
                st.session_state.user_id = "dev_user"
                st.success("✅ Logged in (manual)")
                st.rerun()

from ui.layout import render_sidebar, render_sidebar_footer, logout_user

from utils import calculate_metrics, lbs_to_kg, kg_to_lbs, in_to_cm, cm_to_in, ft_in_to_cm, cm_to_ft_in

def render_onboarding():
    """Render onboarding page with fully reactive and live unit selection."""
    #follow the same color scheme for EpochOne
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 2rem;'><span style='color: #F1C40F;'>👋 Welcome to </span>
            <span style='color: #FF69B4;'>Epoch</span><span style='color: #39FF14;'>One</span>
        </h1>
        """, unsafe_allow_html=True)
          
    # st.title("👋 Welcome to EpochOne!") 
    st.subheader("Let's personalize your experience")

    # 1. Initialize master METRIC state if not present
    if "ob_metric" not in st.session_state:
        st.session_state.ob_metric = {
            "weight": 75.0, "target_weight": 70.0, "height": 175.0,
            "waist": 85.0, "neck": 40.0, "hip": 95.0, "chest": 100.0, "thigh": 55.0
        }

    # 2. Global Unit Toggles (Outside Form for immediate rerun)
    st.info("📏 Set your preferred units. Values will convert live!")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        use_lbs = st.toggle("Use Imperial Weight (lbs)", value=st.session_state.get("ob_use_lbs", False), key="ob_use_lbs")
        w_unit = "lbs" if use_lbs else "kg"
    with t_col2:
        use_in = st.toggle("Use Imperial Measures (in)", value=st.session_state.get("ob_use_in", False), key="ob_use_in")
        m_unit = "inches" if use_in else "cm"
    with t_col3:
        h_unit = st.selectbox("Height Unit", ["cm", "ft & in", "inches"], key="ob_h_unit")

    # 3. Form-less Layout for Reactive Interaction
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Profile")
        name = st.text_input("Full Name", value=st.session_state.get("user", {}).get("name", ""))
        le_col, ri_col = st.columns(2)
        with le_col:
            age = st.number_input("Age", min_value=13, max_value=120, value=25)
            def_w = st.session_state.ob_metric["weight"]
            weight_val = st.number_input(f"Current Weight ({w_unit})", value=float(kg_to_lbs(def_w) if use_lbs else def_w))
        with ri_col:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            def_tw = st.session_state.ob_metric["target_weight"]
            tweight_val = st.number_input(f"Target Weight ({w_unit})", value=float(kg_to_lbs(def_tw) if use_lbs else def_tw))
    
        st.divider()
        st.markdown(f"**Height ({h_unit})**")
        def_h = st.session_state.ob_metric["height"]
        if h_unit == "cm":
            h_h_val = st.number_input("Height (cm)", value=float(def_h), label_visibility="collapsed")
        elif h_unit == "ft & in":
            h_ft, h_in = cm_to_ft_in(def_h)
            hf_col1, hf_col2 = st.columns(2)
            with hf_col1: h_ft_in = st.number_input("ft", min_value=1, max_value=8, value=int(h_ft))
            with hf_col2: h_in_in = st.number_input("in", min_value=0, max_value=11, value=int(h_in))
            h_h_val = (h_ft_in, h_in_in)
        else:
            h_h_val = st.number_input("Height (inches)", value=float(cm_to_in(def_h)), label_visibility="collapsed")
    
    with col2:
        st.markdown("### Measurements")
        lt_col, rt_col = st.columns(2)
        with lt_col:
            def_wa = st.session_state.ob_metric["waist"]
            waist_val = st.number_input(f"Waist ({m_unit})", value=float(cm_to_in(def_wa) if use_in else def_wa))
            def_ch = st.session_state.ob_metric["chest"]
            chest_val = st.number_input(f"Chest ({m_unit})", value=float(cm_to_in(def_ch) if use_in else def_ch))
        with rt_col:
            def_ne = st.session_state.ob_metric["neck"]
            neck_val = st.number_input(f"Neck ({m_unit})", value=float(cm_to_in(def_ne) if use_in else def_ne))
            def_th = st.session_state.ob_metric["thigh"]
            thigh_val = st.number_input(f"Thigh ({m_unit})", value=float(cm_to_in(def_th) if use_in else def_th))

        hip_val = None
        if gender == "Female":
            def_hi = st.session_state.ob_metric["hip"]
            hip_val = st.number_input(f"Hip ({m_unit})", value=float(cm_to_in(def_hi) if use_in else def_hi))
        
        st.divider()
        motive = st.selectbox("Your main goal", ["Weight Loss", "Muscle Gain", "Endurance", "General Health"], key="onboard_motive")
        lifestyle = st.selectbox("Lifestyle type", ["Sedentary", "Lightly Active", "Active", "Very Active"], key="onboard_lifestyle")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        workout_days = st.slider("Workout days a week?", 1, 7, 3)
    with col_s2:
        step_goal = st.number_input("Daily Step Goal", min_value=1000, value=10000)
    
    if st.button("Complete Onboarding", type="primary", use_container_width=True):
        try:
            # 4. Standardize back into metric for final update
            w_kg = weight_val if not use_lbs else lbs_to_kg(weight_val)
            tw_kg = tweight_val if not use_lbs else lbs_to_kg(tweight_val)
            
            if h_unit == "cm": h_cm = h_h_val
            elif h_unit == "ft & in": h_cm = ft_in_to_cm(h_h_val[0], h_h_val[1])
            else: h_cm = in_to_cm(h_h_val)
            
            wa_cm = waist_val if not use_in else in_to_cm(waist_val)
            ne_cm = neck_val if not use_in else in_to_cm(neck_val)
            ch_cm = chest_val if not use_in else in_to_cm(chest_val)
            th_cm = thigh_val if not use_in else in_to_cm(thigh_val)
            hi_cm = (hip_val if not use_in else in_to_cm(hip_val)) if hip_val is not None else None

            # Round to int for API compliance
            h_cm = int(round(h_cm))
            wa_cm = int(round(wa_cm))
            ne_cm = int(round(ne_cm))
            ch_cm = int(round(ch_cm))
            th_cm = int(round(th_cm))
            hi_cm = int(round(hi_cm)) if hi_cm is not None else None

            calc = calculate_metrics(w_kg, h_cm, age, gender.lower(), lifestyle.lower().replace(" ", "_"), wa_cm, ne_cm, hi_cm)
            
            update_payload = {
                "name": name, "age": age, "gender": gender.lower(),
                "units": "imperial" if (use_lbs or use_in) else "metric",
                "weight": w_kg, "height": h_cm, "target_weight": tw_kg,
                "waist": wa_cm, "neck": ne_cm, "chest": ch_cm, "thigh": th_cm, "hip": hi_cm,
                "bmi": calc.get("bmi"), "body_fat_pct": calc.get("body_fat"),
                "lean_body_mass": calc.get("lbm"), "maintenance_calories": calc.get("maintenance"),
                "calorie_target": calc.get("maintenance") - 500 if motive == "Weight Loss" else calc.get("maintenance"),
                "step_goal": step_goal, "motive": motive.lower().replace(" ", "_"),
                "lifestyle_type": lifestyle.lower().replace(" ", "_"), "workout_days_per_week": workout_days,
                "onboarding_complete": True
            }
            
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            resp = requests.put(f"{get_api_base()}/users/profile", json=update_payload, params={"user_id": st.session_state.user_id}, headers=headers)
            
            if resp.status_code == 200:
                st.success("🎉 Profile setup complete!")
                st.session_state.user_profile = resp.json()
                st.rerun()
            else: st.error(f"Update failed: {resp.text}")
        except Exception as e: st.error(f"Error: {e}")

# ============ Main App ============

def main():
    if not is_authenticated():
        # st.title("🏋️ AI Fitness Tracker")
        # st.write("Track your workouts, nutrition, and get AI-powered coaching.")
        login_user()
        return

    # Fetch profile if not in session state
    if "user_profile" not in st.session_state or st.session_state.user_profile is None:
        try:
            api_url = get_api_base()
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            profile_resp = requests.get(
                f"{api_url}/users/profile",
                params={"user_id": st.session_state.user_id},
                headers=headers
            )
            if profile_resp.status_code == 200:
                st.session_state.user_profile = profile_resp.json()
            else:
                st.error("Failed to fetch profile")
        except Exception as e:
            st.error(f"Connection error: {e}")

    profile = st.session_state.get("user_profile", {})
    
    # Check Onboarding
    if not profile.get("onboarding_complete", False):
        render_onboarding()
        return

    # Render centralized sidebar
    render_sidebar()

    # Main dashboard
    st.title("📊 Personal Dashboard")
    
    # Real-time Header
    now = datetime.now()
    col_time1, col_time2 = st.columns([2, 1])
    with col_time1:
        st.subheader(f"Welcome back, {profile.get('name', 'Athlete')}! ✨")
    with col_time2:
        st.markdown(
            f"📅 **{now.strftime('%A, %b %d')}**  \n"
            f"⏰ **{now.strftime('%I:%M %p')}**"
        )
    
    st.divider()

    # Fetch Real Data for Dashboard
    try:
        api_url = get_api_base()
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Today's Activities
        act_resp = requests.get(f"{api_url}/activities/today", params={"user_id": st.session_state.user_id}, headers=headers)
        activities = act_resp.json() if act_resp.status_code == 200 else {}
        
        # Today's Nutrition
        nut_resp = requests.get(f"{api_url}/nutrition/today", params={"user_id": st.session_state.user_id}, headers=headers)
        nutrition = nut_resp.json() if nut_resp.status_code == 200 else {}
        
        # Dashboard Widgets with Live Data
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Steps Today", f"{activities.get('total_activities', 0):,}", "👟")
        with col2:
            target = profile.get("calorie_target", 2200)
            consumed = nutrition.get("calories", 0)
            remaining = target - consumed
            st.metric("Calories", f"{consumed} / {target}", f"{remaining} left" if remaining > 0 else f"{abs(remaining)} over")
        with col3:
            st.metric("Weight", f"{profile.get('weight', '--')} kg", "⚖️")
        with col4:
            st.metric("Streak", f"{profile.get('streak_workout', 0)} days", "🔥")

    except Exception as e:
        st.warning(f"Could not load live stats: {e}")

    st.divider()

    col_details, col_coach = st.columns([1, 1])
    
    with col_details:
        st.subheader("� Your Profile Summary")
        st.write(f"**Goal:** {profile.get('motive', 'Not set').replace('_', ' ').title()}")
        st.write(f"**Lifestyle:** {profile.get('lifestyle_type', 'Not set').replace('_', ' ').title()}")
        st.write(f"**Workout Plan:** {profile.get('workout_days_per_week', 3)} days / week")
        
        if st.button("Edit Profile Settings"):
            st.switch_page("pages/09_⚙️_Settings.py")

    with col_coach:
        st.subheader("🤖 AI Coach Tip")
        try:
            tip_resp = requests.get(f"{api_url}/ai-coach/tip", params={"user_id": st.session_state.user_id}, headers=headers)
            tip = tip_resp.json().get("tip") if tip_resp.status_code == 200 else "Keep pushing towards your goals!"
            st.success(f"💡 **Tip**: {tip}")
        except:
            st.success("💡 Tip: Consistency is key! Keep tracking your progress daily.")
        
        if st.button("Talk to Coach", use_container_width=True):
            st.switch_page("pages/07_🤖_AI_Coach.py")

    render_sidebar_footer()

if __name__ == "__main__":
    main()