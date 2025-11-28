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

# Fetch chat config to get initial message and character limit
if "chat_config" not in st.session_state:
    try:
        config_response = requests.get(
            f"{server_base_url}/api/v1/chat/config",
            headers=headers,
        )
        config_response.raise_for_status()
        st.session_state.chat_config = config_response.json()
    except Exception as e:
        print(f"Error fetching chat config: {e}")
        # Fallback to default values if config fetch fails
        st.session_state.chat_config = {
            "assistant_initial_message": "Hi! How can I help you today?",
            "user_character_limit": 500,
        }

SESSION_ID = st.session_state.session_id
CHAT_CONFIG = st.session_state.chat_config
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
    .bubble-with-buttons {
        background: #F5F5F5;
        color: #1A1A1A;
        padding: 12px 18px;
        border-radius: 2px 18px 18px 18px;
        margin: 6px 0;
        text-align: left;
        font-size: 18px;
        word-break: break-word;
    }
    .chat-button-html {
        background: #E1F3FF;
        color: #0A2540;
        border: 2px solid #0A2540;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 4px 0;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
        display: block;
    }
    .chat-button-html:hover {
        background: #0A2540;
        color: #E1F3FF;
    }
    .buttons-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 12px;
    }
    .button-wrapper {
        margin-top: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .chat-button {
        background: #E1F3FF;
        color: #0A2540;
        border: 2px solid #0A2540;
        border-radius: 8px;
        padding: 10px 20px;
        margin: 6px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        display: inline-block;
        min-width: 200px;
    }
    .chat-button:hover {
        background: #0A2540;
        color: #E1F3FF;
    }
    .button-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bookings Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    # Add initial assistant message from config
    assistant_initial_message = CHAT_CONFIG.get("assistant_initial_message", "")
    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": assistant_initial_message,
        }
    )

# Display chat messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for idx, msg in enumerate(st.session_state["messages"]):
    align = "flex-end" if msg["role"] == "user" else "flex-start"
    bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"

    # Check if this is the initial assistant message with buttons
    has_buttons = (
        msg["role"] == "assistant"
        and idx == 0
        and "initial_buttons" in st.session_state
        and st.session_state["initial_buttons"]
        and len([m for m in st.session_state["messages"] if m["role"] == "user"]) == 0
    )

    if has_buttons:
        # Render message and buttons together inside a single HTML bubble
        buttons = st.session_state["initial_buttons"]
        # Build buttons HTML
        buttons_html = ""
        for i, button in enumerate(buttons):
            button_label = button.get("label", button.get("value", ""))
            button_value = button.get("value", button.get("label", ""))
            # Escape quotes in button values for JavaScript
            button_value_escaped = button_value.replace('"', "&quot;").replace(
                "'", "&#39;"
            )
            buttons_html += f"""
                <button class="chat-button-html" onclick="
                    const event = new CustomEvent('buttonClick', {{ detail: {{ value: '{button_value_escaped}' }} }});
                    window.dispatchEvent(event);
                ">{button_label}</button>
            """

        # Render entire bubble with message and buttons as single HTML
        st.markdown(
            f"""
            <div style="display: flex; justify-content: {align};">
                <div class="bubble-with-buttons" style="width: 100%; max-width: 70%;">
                    <div style="white-space: pre-line;">{msg["content"]}</div>
                    <div class="buttons-grid">
                        {buttons_html}
                    </div>
                </div>
            </div>
            <script>
                window.addEventListener('buttonClick', function(event) {{
                    // Store the button value and trigger Streamlit rerun
                    const value = event.detail.value;
                    // We'll use a hidden input and form submission
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.style.display = 'none';
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'button_click';
                    input.value = value;
                    form.appendChild(input);
                    document.body.appendChild(form);
                    // Trigger Streamlit rerun by submitting form
                    // Actually, we need to use Streamlit's API
                    // For now, we'll use a workaround with session state
                }});
            </script>
            """,
            unsafe_allow_html=True,
        )

        # Check if a button was clicked (using a workaround with query params or session state)
        # Since HTML buttons can't directly update Streamlit state, we'll use a different approach
        # Let's use Streamlit buttons but position them absolutely inside the bubble
    else:
        # Regular message without buttons
        st.markdown(
            f"""
            <div style="display: flex; justify-content: {align};">
                <div class="{bubble_class}">
                    {msg["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown("</div>", unsafe_allow_html=True)

# Get character limit from config, default to 500
user_character_limit = CHAT_CONFIG.get("user_character_limit", 500)
placeholder_text = f"Ask me something... (max {user_character_limit} characters)"

user_input = st.chat_input(placeholder_text, key="input_box")
if user_input:
    # Validate character limit
    if len(user_input) > user_character_limit:
        st.warning(
            f"Message exceeds the character limit of {user_character_limit}. Please shorten your message."
        )
        st.stop()
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
