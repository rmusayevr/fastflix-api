from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websockets import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    The WebSocket endpoint.
    Clients connect to: ws://localhost:8000/api/v1/notifications/ws
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            await websocket.send_text(f"You wrote: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user left the chat")
