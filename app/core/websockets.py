from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections, mapping User IDs to their active sockets.
    """

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to a specific user only."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        """Send to everyone (e.g. New Movie alerts)."""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()
