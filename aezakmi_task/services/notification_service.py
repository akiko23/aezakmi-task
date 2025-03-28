from datetime import datetime
from typing import List, Optional, Protocol

from aezakmi_task.models import Notification
from aezakmi_task.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)


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



class NotificationAnalyzer(Protocol):
    def analyze(self, notification_id: str):
        raise NotImplementedError


class NotificationService:
    def __init__(self, repository: NotificationGateway, notification_analyzer: NotificationAnalyzer):
        self.repository = repository
        self.notification_analyzer = notification_analyzer

    async def create_notification(
        self, notification: NotificationCreate
    ) -> NotificationResponse:
        db_notification = await self.repository.create(notification)
        self.notification_analyzer.analyze(str(db_notification.id))
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

    async def mark_as_read(
        self, notification_id: str,
    ) -> Optional[NotificationResponse]:
        update_data = NotificationUpdate(read_at=datetime.now())
        updated_notification = await self.repository.update(notification_id, update_data)
        if not updated_notification:
            return None
        return NotificationResponse.model_validate(updated_notification)

    async def get_processing_status(self, notification_id: str) -> Optional[str]:
        notification = await self.repository.get(notification_id)
        if not notification:
            return None
        return notification.processing_status
