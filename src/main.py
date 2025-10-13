import os
import uuid

import requests
import streamlit as st

from src.constants import SERVER_BASE_URL
from src.jwt_token import create_jwt_token

st.set_page_config(page_title="My Chatbot", layout="wide")

server_base_url = os.environ.get("SERVER_BASE_URL") or SERVER_BASE_URL

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


SESSION_ID = st.session_state.session_id
print(f"Session ID: {SESSION_ID}")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
USER_EMAIL = os.environ.get("USER_EMAIL", "user@example.com")
USER_GUID = os.environ.get("USER_GUID", str(uuid.uuid4()))

if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = create_jwt_token(
        JWT_SECRET_KEY, user_email=USER_EMAIL, user_guid=USER_GUID
    )

JWT_TOKEN = st.session_state.jwt_token


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

    /* Increase chat font size */
    .stChatMessage p {
        font-size: 18px !important;
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Order Management Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.markdown("</div>", unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask me something...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        with st.spinner("Processing..."):
            try:
                # Create headers with JWT token
                headers = {
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json",
                    "X-Session-Unique-Id": SESSION_ID,
                }

                response = requests.post(
                    f"{server_base_url}/v1/chat",
                    json={"query": user_input},
                    headers=headers,
                )
                bot_reply = response.json()["message"]
            except Exception as e:
                bot_reply = "Sorry for the inconvenience, I am unable to process your request at the moment. Please try again later."
                print(f"Error processing response: {e}")

        message_placeholder.write(bot_reply)

    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
    st.rerun()
