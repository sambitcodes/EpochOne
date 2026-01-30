"""AI Coach chatbot powered by Groq."""
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="AI Coach v3", page_icon="🤖", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🤖 AI Coach v3.1")

# Sleek ChatGPT-style Chat CSS
st.markdown("""
<style>
    /* Reset and Core Layout */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        width: 100% !important;
        padding: 0.6rem 0 !important;
        display: flex !important;
    }

    [data-testid="stChatMessageContent"] {
        padding: 0 !important;
        background-color: transparent !important;
    }

    /* User Message: Anchor and Alignment */
    div[data-testid="stChatMessage"]:has(.user-anchor) {
        flex-direction: row-reverse !important;
        justify-content: flex-start !important;
    }

    div[data-testid="stChatMessage"]:has(.user-anchor) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, rgba(232, 65, 24, 0.2) 0%, rgba(98, 0, 238, 0.15) 100%) !important;
        border: 1px solid rgba(232, 65, 24, 0.4) !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 12px 18px !important;
        margin-right: 12px !important;
        margin-left: 15% !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        color: #f1f5f9 !important;
        width: auto !important;
        max-width: 80% !important;
        min-width: 80px !important;
    }

    /* Assistant Message: Anchor and Alignment */
    div[data-testid="stChatMessage"]:has(.assistant-anchor) {
        flex-direction: row !important;
        justify-content: flex-start !important;
    }

    div[data-testid="stChatMessage"]:has(.assistant-anchor) [data-testid="stChatMessageContent"] {
        background: rgba(30, 41, 59, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 14px 20px !important;
        margin-left: 12px !important;
        margin-right: 10% !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        color: #f1f5f9 !important;
        width: auto !important;
        max-width: 85% !important;
        min-width: 250px !important; /* Prevents narrow collapse */
        line-height: 1.6 !important;
    }

    /* Clean Avatars */
    [data-testid="stChatMessageAvatar"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }

    /* Hide anchors */
    .user-anchor, .assistant-anchor {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None

def fetch_threads():
    try:
        response = requests.get(
            f"{get_api_base()}/ai-coach/threads",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def load_thread(thread_id):
    try:
        response = requests.get(
            f"{get_api_base()}/ai-coach/threads/{thread_id}/messages",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if response.status_code == 200:
            st.session_state.chat_history = response.json()
            st.session_state.current_thread_id = thread_id
            st.rerun()
    except Exception as e:
        st.error(f"Failed to load thread: {e}")

def delete_thread(thread_id):
    try:
        response = requests.delete(
            f"{get_api_base()}/ai-coach/threads/{thread_id}",
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )
        if response.status_code == 200:
            if st.session_state.current_thread_id == thread_id:
                st.session_state.current_thread_id = None
                st.session_state.chat_history = []
            st.rerun()
    except Exception as e:
        st.error(f"Failed to delete thread: {e}")

# Sidebar for Library & Settings
with st.sidebar:
    st.markdown("### 📚 Chat Library")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_thread_id = None
        st.session_state.chat_history = []
        st.rerun()
        
    st.divider()
    
    threads = fetch_threads()
    if not threads:
        st.caption("No saved conversations yet.")
    else:
        for thread in threads:
            col_t, col_d = st.columns([4, 1])
            with col_t:
                # Highlight active thread
                is_active = st.session_state.current_thread_id == thread['id']
                label = f"**{thread['title']}**" if is_active else thread['title']
                if st.button(label, key=f"t_{thread['id']}", use_container_width=True):
                    load_thread(thread['id'])
            with col_d:
                if st.button("🗑️", key=f"del_{thread['id']}", help="Delete this thread"):
                    delete_thread(thread['id'])

    st.divider()
    st.subheader("Coach Settings")

    mode = st.selectbox(
        "Mode",
        ["General", "Training Plan", "Nutrition", "Recovery", "Motivation", "Explain Data"]
    )

    model_options = [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
        {"id": "groq/compound", "name": "Compound"},
        {"id": "openai/gpt-oss-120b", "name": "OpenAI GPT OSS 120B"}
    ]
    model_ids = [m["id"] for m in model_options]
    model_names = [m["name"] for m in model_options]
    
    selected_model_idx = st.selectbox(
        "AI Model",
        range(len(model_names)),
        format_func=lambda x: model_names[x]
    )
    model = model_ids[selected_model_idx]

    st.divider()
    st.caption("⚠️ Not medical advice. Always consult professionals.")

import time
import pandas as pd

def clean_ai_text(text):
    """Strip structured JSON data from the visible text."""
    if "[ACTION_JSON_START]" in text:
        text = text.split("[ACTION_JSON_START]")[0]
    # Fallback for old style or just in case
    if "{" in text and '"action_type":' in text:
        text = text.split("{")[0]
    return text.strip()

def stream_text(text, delay=0.01):
    """Simulate streaming text."""
    text = clean_ai_text(text)
    placeholder = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        placeholder.markdown(full_text + "▌")
        time.sleep(delay)
    placeholder.markdown(full_text)

# Get user picture for avatar
user_avatar = st.session_state.get("user", {}).get("picture")
if not user_avatar and st.session_state.get("user_profile"):
    user_avatar = st.session_state.user_profile.get("picture")

def render_ai_action(action_data):
    """Render structured AI actions stealthily in expanders."""
    if not action_data:
        return
    
    if isinstance(action_data, list):
        for act in action_data:
            render_ai_action(act)
        return
    
    action_type = action_data.get("action_type")
    details = action_data.get("details", {})
    
    # Map types to premium titles
    titles = {
        "create_workout": f"🏋️ Generated Workout: {details.get('name', 'New Session')}",
        "update_macros": "🥗 New Macro Targets",
        "plan_week": "📅 Your Weekly Schedule"
    }
    title = titles.get(action_type, f"📋 Proposed {action_type.replace('_', ' ').title()}")

    with st.expander(title, expanded=True):
        if action_type == "create_workout":
            exercises = details.get("exercises", [])
            if exercises:
                df = pd.DataFrame(exercises)
                st.table(df)
        
        elif action_type == "update_macros":
            col1, col2, col3 = st.columns(3)
            col1.metric("Protein", f"{details.get('protein', 0)}g")
            col2.metric("Carbs", f"{details.get('carbs', 0)}g")
            col3.metric("Fat", f"{details.get('fat', 0)}g")
            st.caption(f"**Target Calories**: {details.get('calories', 0)} kcal")
            
        elif action_type == "plan_week":
            days = details.get("days", {})
            if isinstance(days, dict):
                for day, activity in days.items():
                    st.write(f"**{day.title()}**: {activity}")
            elif isinstance(days, list):
                for item in days:
                    if isinstance(item, dict):
                        d = item.get("day", "Day")
                        a = item.get("activity", item.get("task", ""))
                        st.write(f"**{d}**: {a}")
                    else:
                        st.write(f"- {item}")
        
        else:
            st.json(action_data)

# Display chat history
for i, message in enumerate(st.session_state.chat_history):
    if message["role"] == "user":
        with st.chat_message("user", avatar=user_avatar):
            st.markdown('<div class="user-anchor"></div>', unsafe_allow_html=True)
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown('<div class="assistant-anchor"></div>', unsafe_allow_html=True)
            st.markdown(clean_ai_text(message["content"]))
            if message.get("actions"):
                render_ai_action(message["actions"])

# Input area
user_input = st.chat_input("Chat with your AI coach...")

if user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar=user_avatar):
        st.markdown('<div class="user-anchor"></div>', unsafe_allow_html=True)
        st.write(user_input)

    # Get coach response
    try:
        payload = {
            "message": user_input,
            "mode": mode.lower(),
            "model": model,
            "thread_id": st.session_state.current_thread_id
        }

        response = requests.post(
            f"{get_api_base()}/ai-coach/chat",
            json=payload,
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            text = data.get("message", "")
            actions = data.get("actions")
            thread_id = data.get("thread_id")

            # Update thread ID if new
            if not st.session_state.current_thread_id:
                st.session_state.current_thread_id = thread_id

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown('<div class="assistant-anchor"></div>', unsafe_allow_html=True)
                # Stream the text
                stream_text(text)
                
                # Render actions
                if actions:
                    render_ai_action(actions)

            coach_response = {
                "role": "assistant",
                "content": text,
                "actions": actions
            }
            st.session_state.chat_history.append(coach_response)
            
        else:
            st.error(f"Error: {response.text}")

    except Exception as e:
        st.error(f"Failed to get response: {e}")

render_sidebar_footer()
