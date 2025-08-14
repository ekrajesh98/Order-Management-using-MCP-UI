import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

from constants import SERVER_BASE_URL

st.set_page_config(page_title="My Chatbot", layout="wide")
load_dotenv()

server_base_url = os.environ.get("SERVER_BASE_URL") or SERVER_BASE_URL

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

SESSION_ID = st.session_state.session_id


# Center the chat, remove sidebar, adjust widths
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
                response = requests.post(
                    f"{server_base_url}/chat",
                    json={"query": user_input, "session_id": SESSION_ID},
                )
                bot_reply = response.json()["message"]
            except Exception as e:
                bot_reply = "Sorry for the inconvenience, I am unable to process your request at the moment. Please try again later."
                print(f"Error processing response: {e}")

        message_placeholder.write(bot_reply)

    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
    st.rerun()
