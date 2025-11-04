import os

import requests
import streamlit as st

from src.constants import SERVER_BASE_URL

st.set_page_config(page_title="My Chatbot", layout="wide")

server_base_url = os.environ.get("SERVER_BASE_URL") or SERVER_BASE_URL


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
USER_EMAIL = os.environ.get("USER_EMAIL")
CLIENT_UUID = os.environ.get("CLIENT_UUID")
USER_GUID = os.environ.get("USER_GUID")

headers = {
    "auth-email": USER_EMAIL,
    "client-uuid": CLIENT_UUID,
    "auth-uuid": USER_GUID,
    "Content-Type": "application/json",
}

if "session_id" not in st.session_state:
    response = requests.post(
        f"{server_base_url}/api/v1/session",
        headers=headers,
    )
    st.session_state.session_id = response.json().get("session_uuid")


SESSION_ID = st.session_state.session_id
print(f"Session ID: {SESSION_ID}")


st.markdown(
    """
    <style>
    /* Remove sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Page content full height */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem; /* leave room for fixed input */
        max-width: 800px; /* control chat width */
        margin: auto; /* center horizontally */
    }

    /* Chat container scrollable */
    .chat-container {
        max-height: calc(100vh - 200px);
        overflow-y: auto;
        padding-right: 10px;
    }

    /* Fix the input at bottom center */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 500px !important;
        margin: 0;
        padding: 0;
        background: transparent;
        border: none;
        z-index: 1000;
    }
    .stChatInputContainer > div {
        width: 100% !important;
    }
    .stChatInputContainer textarea {
        font-size: 18px !important;
        padding: 12px !important;
        min-height: 60px !important;
        text-align: center;
        width: 100% !important;
        box-sizing: border-box;
    }
    .stChatInputContainer textarea::placeholder {
        text-align: center;
    }

    .user-bubble {
        background: #E1F3FF;            /* Soft light blue */
        color: #0A2540;                 /* Dark navy text for contrast */
        padding: 12px 18px;
        border-radius: 18px 2px 18px 18px;
        max-width: 70%;
        margin: 6px 0;
        text-align: left;
        font-size: 18px;
        word-break: break-word;
    }
    .bot-bubble {
        background: #F5F5F5;            /* Light neutral gray */
        color: #1A1A1A;                 /* Almost black text */
        padding: 12px 18px;
        border-radius: 2px 18px 18px 18px;
        max-width: 70%;
        margin: 6px 0;
        text-align: left;
        font-size: 18px;
        word-break: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bookings Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    align = "flex-end" if msg["role"] == "user" else "flex-start"
    bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
    st.markdown(
        f'''
        <div style="display: flex; justify-content: {align};">
            <div class="{bubble_class}">
                {msg["content"]}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

user_input = st.chat_input("Ask me something...", key="input_box")
if user_input:
    # append user message immediately
    st.session_state["messages"].append({"role": "user", "content": user_input})
    # stash the pending query for phase 2
    st.session_state["pending_query"] = user_input
    # force a rerun so the user bubble appears right away
    st.rerun()

# 2) Phase 2: after rerun, detect pending and call server
if "pending_query" in st.session_state:
    query = st.session_state.pop("pending_query")
    with st.spinner("Processing…"):
        try:
            headers = {
                **headers,
                "X-Session-Unique-Id": SESSION_ID,
            }
            response = requests.post(
                f"{server_base_url}/api/v1/chat",
                json={"query": query},
                headers=headers,
            )
            bot_reply = response.json()["message"]
        except Exception as e:
            bot_reply = (
                "Sorry for the inconvenience, I am unable to process "
                "your request at the moment. Please try again later."
            )
            print(f"Error processing response: {e}")
    # append assistant response and rerun to show it
    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
    st.rerun()
