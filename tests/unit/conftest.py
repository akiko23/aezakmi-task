from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from aezakmi_task.services.notification_service import NotificationService, NotificationGateway, NotificationAnalyzer


@pytest.fixture(scope="function")
def config_mock() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def robot_facade_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope="function")
def notification_repository_mock() -> AsyncMock:
    return AsyncMock()

@pytest.fixture(scope="function")
def notification_analyzer_mock() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def notification_service(
        notification_repository_mock: AsyncMock,
        notification_analyzer_mock: Mock
):
    return NotificationService(
        repository=cast(NotificationGateway, notification_repository_mock),
        notification_analyzer=cast(NotificationAnalyzer, notification_analyzer_mock),
    )
