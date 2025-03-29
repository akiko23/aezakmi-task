from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from aezakmi_task.models.notification import Notification
from aezakmi_task.schemas.notification import NotificationCreate, NotificationUpdate


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
            self,
            skip: int = 0,
            limit: int = 10,
            status: Optional[str] = None,
            user_id: Optional[str] = None
    ) -> tuple[list[Notification], int]:
        base_query = select(Notification)
        if status:
            base_query = base_query.filter(Notification.processing_status == status)
        if user_id:
            base_query = base_query.filter(Notification.user_id == user_id)

        data_query = base_query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        notifications = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return notifications, total

    async def update(
        self, notification: Notification, notification_update: NotificationUpdate
    ) -> Notification:
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
