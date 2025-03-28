import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aezakmi_task.models import Notification
from aezakmi_task.schemas.notification import NotificationCreate


@pytest.mark.asyncio
async def test_health(test_client: AsyncClient):
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}


@pytest.mark.asyncio
async def test_create_notification(test_client: AsyncClient):
    new_obj = NotificationCreate(title="title", text="blah blah", user_id=str(uuid.uuid4()))

    response = await test_client.post('/api/v1/notifications/', content=new_obj.model_dump_json())
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_notifications(test_client: AsyncClient, db_session: AsyncSession):
    user_id = uuid.uuid4()

    existing_notifications = [
        Notification(
            id=str(uuid.uuid4()),
            title="n1",
            text="hello",
            user_id=user_id,
            category="info",
            confidence=0.9,
            processing_status="completed"
        ),
        Notification(
            id=str(uuid.uuid4()),
            title="n2",
            text="hello error",
            user_id=user_id,
            category="critical",
            confidence=0.9,
            processing_status="completed"
        ),
        Notification(
            id=str(uuid.uuid4()),
            title="n3",
            text="Warning! Its probably dangerous",
            user_id=user_id,
            category="warning",
            confidence=0.9,
            processing_status="completed"
        )
    ]
    for notification in existing_notifications:
        db_session.add(notification)
    await db_session.commit()

    response = await test_client.get('/api/v1/notifications/')
    assert response.status_code == 200
    assert len(response.json()['results']) == len(existing_notifications)


@pytest.mark.asyncio
async def test_get_notification(test_client: AsyncClient, db_session: AsyncSession):
    user_id = uuid.uuid4()

    existing_notification = Notification(
        id=str(uuid.uuid4()),
        title="n1",
        text="hello hello!",
        user_id=user_id,
        category="info",
        confidence=0.9,
            processing_status="completed"
    )
    db_session.add(existing_notification)
    await db_session.commit()

    response = await test_client.get(f'/api/v1/notifications/{existing_notification.id}')
    assert response.status_code == 200
    assert response.json()['text'] == existing_notification.text
