"""Layout utilities and structure."""
import streamlit as st
from typing import Optional, List, Callable

def logout_user():
    """Logout user."""
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.user_profile = None
    st.success("✅ Logged out")
    st.switch_page("Home.py")

def render_sidebar():
    """Render consistent sidebar with Profile Pic, XP, and Logout."""
    profile = st.session_state.get("user_profile")
    if not profile:
        return

    with st.sidebar:
        st.title("🏋️ EpochOne")
        
        # 1. Profile Picture
        if profile.get("picture"):
            st.image(profile["picture"], width=100)
        else:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
            
        # 2. First Name & XP
        name = profile.get("name", "User")
        first_name = name.split()[0]
        st.markdown(f"### Hello, {first_name}! 👋")
        
        st.markdown(f"**Level {profile.get('level', 1)}**")
        st.progress(min((profile.get("xp", 0) % 1000) / 1000, 1.0))
        st.caption(f"XP: {profile.get('xp', 0)}")
        
        st.divider()
        # Pages will be listed here automatically by Streamlit
        
        # Logout button will appear at the bottom of the sidebar naturally as code continues
        # But we want it explicitly at the end. Note: st.sidebar code appends.
        # To ensure it's at the VERY bottom, we might need a container or just trust the call order.

def render_sidebar_footer():
    """Render the logout button at the bottom of the sidebar."""
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout_btn"):
            logout_user()

def main_content_area(func: Callable):
    """
    Decorator for main content area with consistent padding.
    
    Args:
        func: Page render function
    """
    def wrapper():
        st.markdown("""
        <style>
            [data-testid="stMainBlockContainer"] {
                padding-top: 2rem;
            }
        </style>
        """, unsafe_allow_html=True)
        func()
    return wrapper

def two_column_layout(col1_content: Callable, col2_content: Callable, ratio: tuple = (1, 1)):
    """
    Two-column layout helper.
    
    Args:
        col1_content: Function for left column
        col2_content: Function for right column
        ratio: Column width ratio
    """
    col1, col2 = st.columns(ratio)
    with col1:
        col1_content()
    with col2:
        col2_content()

def three_column_layout(
    col1_content: Callable,
    col2_content: Callable,
    col3_content: Callable,
    ratio: tuple = (1, 1, 1)
):
    """
    Three-column layout helper.
    
    Args:
        col1_content: Function for left column
        col2_content: Function for middle column
        col3_content: Function for right column
        ratio: Column width ratio
    """
    col1, col2, col3 = st.columns(ratio)
    with col1:
        col1_content()
    with col2:
        col2_content()
    with col3:
        col3_content()

def tabs_container(tabs: dict):
    """
    Tab container helper.
    
    Args:
        tabs: Dict of tab_name -> render_function
    """
    tab_list = st.tabs(list(tabs.keys()))
    for tab, (name, func) in zip(tab_list, tabs.items()):
        with tab:
            func()
