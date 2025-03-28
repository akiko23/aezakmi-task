from datetime import datetime
from typing import List, Optional, Protocol

from app.models import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.tasks.ai_tasks import process_notification_analysis


class NotificationGateway(Protocol):
    async def create(self, notification: NotificationCreate) -> Notification:
        raise NotImplementedError

    async def get(self, notification_id: str) -> Optional[Notification]:
        raise NotImplementedError

    async def get_all(
        self, skip: int = 0, limit: int = 10, status: str = None
    ) -> List[Notification]:
        raise NotImplementedError

    async def update(
        self, notification_id: str, notification_update: NotificationUpdate
    ) -> Optional[Notification]:
        raise NotImplementedError

    async def update_status(
        self, notification_id: str, status: str
    ) -> Optional[Notification]:
        raise NotImplementedError

    async def delete(self, notification_id: str) -> bool:
        raise NotImplementedError


class NotificationService:
    def __init__(self, repository: NotificationGateway):
        self.repository = repository

    async def create_notification(
        self, notification: NotificationCreate
    ) -> NotificationResponse:
        db_notification = await self.repository.create(notification)
        process_notification_analysis.delay(str(db_notification.id))
        return NotificationResponse.model_validate(db_notification)

    async def get_notification(self, notification_id: str) -> Optional[NotificationResponse]:
        notification = await self.repository.get(notification_id)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def get_notifications(
        self, skip: int = 0, limit: int = 10, status: str = None
    ) -> List[NotificationResponse]:
        notifications = await self.repository.get_all(skip=skip, limit=limit, status=status)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def update_notification(
        self, notification_id: str, notification_update: NotificationUpdate
    ) -> Optional[NotificationResponse]:
        notification_update.read_at = datetime.now()
        updated_notification = await self.repository.update(notification_id, notification_update)
        if not updated_notification:
            return None
        return NotificationResponse.model_validate(updated_notification)

    async def mark_as_read(self, notification_id: str) -> Optional[NotificationResponse]:
        from datetime import datetime
        update_data = NotificationUpdate(read_at=datetime.now())
        return await self.update_notification(notification_id, update_data)

    async def delete_notification(self, notification_id: str) -> bool:
        return await self.repository.delete(notification_id)

    async def get_processing_status(self, notification_id: str) -> Optional[str]:
        notification = await self.repository.get(notification_id)
        if not notification:
            return None
        return notification.processing_status
