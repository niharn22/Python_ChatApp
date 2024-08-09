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
                pass

# Start WebSocket listener in a background thread
if 'ws_thread' not in st.session_state:
    ws_thread = threading.Thread(target=websocket_listener)
    ws_thread.daemon = True
    ws_thread.start()
    st.session_state['ws_thread'] = ws_thread

# Chat Input
st.title("ChatUp")
user_name = st.text_input("Enter your name:", key="name")
new_message = st.text_input("Enter your message:", key="message")

# Send message
if st.button("Send"):
    if user_name and new_message:
        message = f"{user_name}: {new_message}"
        ws = websocket.WebSocket()
        ws.connect(WS_URL)
        ws.send(message)
        ws.close()

# Display messages
if 'new_message' in st.session_state and st.session_state['new_message']:
    st.session_state['new_message'] = False
    st.experimental_rerun()

st.write("**Chat Messages**")
for msg in fetch_messages():
    st.write(f"**{msg['user']}**: {msg['message']}")
