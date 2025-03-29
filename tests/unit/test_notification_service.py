import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from aezakmi_task.models import Notification
from aezakmi_task.schemas.notification import NotificationCreate, ManyNotificationsResponse
from aezakmi_task.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_create_notification(
        notification_service: NotificationService,
        notification_analyzer_mock: Mock,
        notification_repository_mock: AsyncMock,
):
    new_notification = Notification(
        id=uuid.uuid4(),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending"
    )
    notification_repository_mock.create.return_value = new_notification

    notification_create = NotificationCreate(
        title="title",
        text="text",
        user_id=uuid.uuid4()
    )
    await notification_service.create_notification(notification=notification_create)

    notification_repository_mock.create.assert_called_once_with(notification_create)
    notification_analyzer_mock.analyze.assert_called_once_with(str(new_notification.id))


@pytest.mark.asyncio
async def test_get_notification(
        notification_service: NotificationService,
        notification_repository_mock: AsyncMock,
):
    existing_notification = Notification(
        id=uuid.uuid4(),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending"
    )
    notification_repository_mock.get.return_value = existing_notification

    await notification_service.get_notification(existing_notification.id)
    notification_repository_mock.get.assert_called_once_with(existing_notification.id)


@pytest.mark.asyncio
async def test_get_all_notifications(
        notification_service: NotificationService,
        notification_repository_mock: AsyncMock,
):
    limit, offset = 10, 0

    existing_notifications = [Notification(
        id=uuid.UUID(int=uuid.uuid4().int + i),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending"
    ) for i in range(10)]
    notification_repository_mock.get_all.return_value = (existing_notifications, len(existing_notifications))

    await notification_service.get_notifications(limit=limit, skip=offset)
    notification_repository_mock.get_all.assert_called_once_with(
        skip=offset,
        limit=limit,
        status=None,
        user_id=None,
    )


@pytest.mark.asyncio
async def test_get_only_completed_notifications(
        notification_service: NotificationService,
        notification_repository_mock: AsyncMock,
):
    limit, offset = 10, 0

    pending_notifications = [Notification(  # noqa
        id=uuid.UUID(int=uuid.uuid4().int + i),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending"
    ) for i in range(10)]
    completed_notifications = [Notification(
        id=uuid.UUID(int=uuid.uuid4().int + i),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="completed"
    ) for i in range(5)]
    notification_repository_mock.get_all.return_value = (completed_notifications, len(completed_notifications))

    await notification_service.get_notifications(limit=limit, skip=offset, status="completed")
    notification_repository_mock.get_all.assert_called_once_with(
        skip=offset,
        limit=limit,
        status="completed",
        user_id=None,
    )


@pytest.mark.asyncio
async def test_get_notification_status(
        notification_service: NotificationService,
        notification_repository_mock: AsyncMock,
):
    existing_notification = Notification(
        id=uuid.uuid4(),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending"
    )
    notification_repository_mock.get.return_value = existing_notification

    status = await notification_service.get_processing_status(existing_notification.id)
    notification_repository_mock.get.assert_called_once_with(existing_notification.id)

    assert status == existing_notification.processing_status


@pytest.mark.asyncio
async def test_mark_notification_as_read(
        notification_service: NotificationService,
        notification_repository_mock: AsyncMock,
):
    existing_notification = Notification(
        id=uuid.uuid4(),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending",
        category="info",
        read_at=None  # noqa
    )

    notification_repository_mock.get.return_value = existing_notification

    updated_notification = Notification(
        id=uuid.uuid4(),
        title="title",
        text="text",
        user_id=uuid.uuid4(),
        created_at=datetime.now(),
        processing_status="pending",
        category="info",
        read_at=datetime.now()
    )
    notification_repository_mock.update.return_value = updated_notification

    updated_notification = await notification_service.mark_as_read(existing_notification.id)
    notification_repository_mock.update.assert_called_once()

    assert updated_notification.read_at is not None
