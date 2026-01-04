from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select
from app.core.websockets import manager
from app.core.security import verify_token_access
from app.db.session import AsyncSessionLocal
from app.models.user import UserModel

router = APIRouter()


async def get_user_from_socket(token: str) -> int | None:
    """
    1. Validates JWT signature.
    2. Checks DB to ensure user is active/exists.
    """
    payload = verify_token_access(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(UserModel).where(UserModel.id == int(user_id)))
        user = result.scalars().first()

        if user and user.is_active:
            return user.id

    return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, token: str = Query(...)
):
    user_id = await get_user_from_socket(token)

    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connection accepted
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)


# --- Test Endpoint for Targeted Notifications ---
@router.post("/test-trigger/{user_id}")
async def trigger_private_notification(user_id: int, message: str):
    """
    Simulates a system event (like 'Your export is ready')
    sending a message ONLY to this specific user.
    """
    await manager.send_personal_message(f"🔔 Private: {message}", user_id)
    return {"status": "Message sent"}
