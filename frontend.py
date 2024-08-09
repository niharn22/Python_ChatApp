import streamlit as st
import websocket
import threading
import json
import requests

# API and WebSocket URLs
API_URL = "http://localhost:8000/messages"
WS_URL = "ws://localhost:8000/ws"

# Initialize chat messages
messages = []

def fetch_messages():
    """Fetch chat messages from the server."""
    response = requests.get(API_URL)
    return response.json()

def websocket_listener():
    """Listen for messages from the WebSocket server."""
    ws = websocket.WebSocket()
    ws.connect(WS_URL)
    while True:
        msg = ws.recv()
        if msg:  # Check if the message is not empty
            try:
                messages.append(json.loads(msg))
                st.session_state['new_message'] = True  # Trigger Streamlit rerun
            except json.JSONDecodeError:
                pass  # Do nothing if a JSON decode error occurs

# Start WebSocket listener in a background thread
if 'ws_thread' not in st.session_state:
    ws_thread = threading.Thread(target=websocket_listener)
    ws_thread.daemon = True
    ws_thread.start()
    st.session_state['ws_thread'] = ws_thread

# Create two columns
col1, col2 = st.columns([0.3, 0.7])

# Center the content in the left column with better alignment
with col1:
    st.markdown(
        """
        <style>
        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%; /* Full width */
            position: fixed; /* Fix to the top */
            top: 0;
            left: 0;
            padding: 10px;
            background: white; /* Optional: Background color for visibility */
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Optional: Shadow for better visibility */
        }
        .content-wrapper {
            width: 300px; /* Adjust as needed */
        }
        </style>
        <div class="header-container">
        <div class="content-wrapper">
        """,
        unsafe_allow_html=True
    )
    
    st.title("Chat Input")
    user_name = st.text_input("Enter your name:", key="name")
    new_message = st.text_input("Enter your message:", key="message")
    if st.button("Send"):
        if user_name and new_message:
            message = {"user": user_name, "message": new_message}
            ws = websocket.WebSocket()
            ws.connect(WS_URL)
            ws.send(json.dumps(message))
            ws.close()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Display chat messages with a full translucent background for each message in the right column
with col2:
    st.title("Chat Messages")
    chat_container = st.empty()

    if 'new_message' in st.session_state and st.session_state['new_message']:
        st.session_state['new_message'] = False
        st.experimental_rerun()

    with chat_container.container():
        for msg in fetch_messages():
            st.markdown(
                f"<div style='background-color: rgba(135, 206, 235, 0.3); padding: 10px; margin-bottom: 10px; border-radius: 10px;'>"
                f"<p style='margin: 0; font-weight: bold;'>{msg['user']}</p>"
                f"<p style='margin: 0;'>{msg['message']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
