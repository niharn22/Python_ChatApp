from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from typing import List

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Store active WebSocket connections
clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            user, message = data.split(": ", 1)
            save_message(user, message)
            # Broadcast the message to all connected clients
            for client in clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.get("/messages")
async def get_messages():
    return load_messages()
