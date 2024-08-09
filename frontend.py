import streamlit as st
import json
import time
from pathlib import Path

# File to store chat messages
CHAT_FILE = Path("chat_data.json")

# Initialize the chat file
if not CHAT_FILE.exists():
    CHAT_FILE.write_text(json.dumps([]))

def load_messages():
    with CHAT_FILE.open("r") as f:
        return json.load(f)

def save_message(user, message):
    messages = load_messages()
    messages.append({"user": user, "message": message})
    with CHAT_FILE.open("w") as f:
        json.dump(messages, f)

# Function to display messages
def display_messages():
    chat_box = st.empty()
    with chat_box.container():
        messages = load_messages()
        for msg in messages:
            st.write(f"**{msg['user']}**: {msg['message']}")

# Chat Input
st.title("Real-time Chat Service")
user_name = st.text_input("Enter your name:", key="name")
new_message = st.text_input("Enter your message:", key="message")

if st.button("Send"):
    if user_name and new_message:
        save_message(user_name, new_message)
        st.rerun()

# Display chat messages in real-time
display_messages()

# Continuously update the chat display every 2 seconds
while True:
    time.sleep(2)
    st.rerun()
