"""AI Coach chatbot powered by Groq."""
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="AI Coach", page_icon="🤖", layout="wide")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("Home.py")

from ui.layout import render_sidebar, render_sidebar_footer
from ui.styles import apply_theme
apply_theme()
render_sidebar()

st.title("🤖 AI Coach")

from utils import get_api_base

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for settings
with st.sidebar:
    st.subheader("Coach Settings")

    mode = st.selectbox(
        "Mode",
        ["General", "Training Plan", "Nutrition", "Recovery", "Motivation", "Explain Data"]
    )

    model = st.selectbox(
        "AI Model",
        [
            "llama-3.3-70b-versatile",
            "groq/compound",
            "openai/gpt-oss-120b",
            "llama-3.1-70b-versatile",
            "llama3-70b-8192",
            "mixtral-8x7b-32768"
        ]
    )

    st.divider()
    st.caption("⚠️ Not medical advice. Always consult professionals.")

# Main chat area
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# Display chat history
for i, message in enumerate(st.session_state.chat_history):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

            # Show actions if present
            if message.get("actions"):
                with st.expander("📋 Suggested Actions"):
                    actions = message["actions"]
                    st.json(actions)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Approve", key=f"approve_hist_{i}"):
                            st.info("Action approved!")

                    with col2:
                        if st.button("❌ Skip", key=f"skip_hist_{i}"):
                            st.info("Action skipped")

# Input area
user_input = st.chat_input("Chat with your AI coach...")

if user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Get coach response
    try:
        payload = {
            "message": user_input,
            "mode": mode.lower(),
            "model": model
        }

        response = requests.post(
            f"{get_api_base()}/ai-coach/chat",
            json=payload,
            params={"user_id": st.session_state.user_id},
            headers=get_headers()
        )

        if response.status_code == 200:
            data = response.json()

            coach_response = {
                "role": "assistant",
                "content": data.get("message", ""),
                "actions": data.get("actions")
            }

            st.session_state.chat_history.append(coach_response)

            with st.chat_message("assistant"):
                st.write(coach_response["content"])

                if coach_response["actions"]:
                    with st.expander("📋 Suggested Actions"):
                        st.json(coach_response["actions"])

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Approve", key="approve_new"):
                                st.success("Action approved!")

                        with col2:
                            if st.button("❌ Skip", key="skip_new"):
                                st.info("Action skipped")

        else:
            st.error(f"Error: {response.text}")

    except Exception as e:
        st.error(f"Failed to get response: {e}")

    st.rerun()

render_sidebar_footer()
