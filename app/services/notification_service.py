from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import NotificationModel
from app.core.websockets import manager


class NotificationService:
    @staticmethod
    async def send_notification(user_id: int, message: str, db: AsyncSession):
        """
        1. Save to Database (Persistence)
        2. Push to WebSocket (Real-time)
        """
        notification = NotificationModel(user_id=user_id, message=message)
        db.add(notification)
        await db.commit()

        await manager.send_personal_message(message, user_id)

    @staticmethod
    async def broadcast_notification(message: str, db: AsyncSession):
        """
        Warning: For 10,000 users, don't do this in a loop synchronously.
        Use Celery for mass inserts. For now (learning), this is fine.
        """
        await manager.broadcast(message)

    @staticmethod
    async def get_user_notifications(user_id: int, db: AsyncSession, skip=0, limit=20):
        query = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        return result.scalars().all()
