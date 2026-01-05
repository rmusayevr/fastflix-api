import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import NotificationModel
from app.core.redis import get_redis_client


class NotificationService:
    @staticmethod
    async def send_notification(user_id: int, message: str, db: AsyncSession):
        notification = NotificationModel(user_id=user_id, message=message)
        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        try:
            redis_client = get_redis_client()

            payload = {"user_id": user_id, "message": message}
            await redis_client.publish("notifications", json.dumps(payload))

            await redis_client.close()

        except Exception as e:
            print(f"❌ Redis Publish Error: {e}")

        return notification

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
