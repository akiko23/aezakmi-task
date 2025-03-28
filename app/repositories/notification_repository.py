from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from typing import List, Optional

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.model_dump())
        self.session.add(db_notification)
        await self.session.commit()
        await self.session.refresh(db_notification)
        return db_notification

    async def get(self, notification_id: str) -> Optional[Notification]:
        result = await self.session.execute(
            select(Notification).filter(Notification.id == notification_id)
        )
        return result.scalars().first()

    async def get_all(
        self, skip: int = 0, limit: int = 10, status: str = None
    ) -> List[Notification]:
        query = select(Notification)
        if status:
            query = query.filter(Notification.processing_status == status)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, notification_id: str, notification_update: NotificationUpdate
    ) -> Optional[Notification]:
        notification = await self.get(notification_id)
        if not notification:
            return None
        notification.read_at = notification_update.read_at
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def update_status(
        self, notification_id: str, status: str
    ) -> Optional[Notification]:
        notification = await self.get(notification_id)
        if not notification:
            return None
        notification.processing_status = status
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def update_analysis(
        self,
        notification_id: str,
        category: str,
        confidence: float,
        status: str
    ) -> Optional[Notification]:
        notification = await self.get(notification_id)
        if not notification:
            return None
        notification.category = category
        notification.confidence = confidence
        notification.processing_status = status
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
