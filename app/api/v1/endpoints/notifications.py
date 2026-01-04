from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.core.security import verify_token_access
from app.core.websockets import manager
from app.db.session import AsyncSessionLocal
from app.models.user import UserModel
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse

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
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id = await get_user_from_socket(token)

    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)


@router.post("/test-trigger/{user_id}")
async def trigger_private_notification(
    user_id: int, message: str, db: AsyncSession = Depends(get_db)
):
    """
    Simulates a system event (like 'Your export is ready')
    sending a message ONLY to this specific user.
    """
    await NotificationService.send_notification(user_id, message, db)
    return {"status": "Notification sent and saved"}


@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch notification history."""
    return await NotificationService.get_user_notifications(
        current_user.id, db, skip, limit
    )
