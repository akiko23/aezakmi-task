from contextlib import suppress
from typing import Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import Response
from redis.asyncio import Redis
from starlette.websockets import WebSocket

from aezakmi_task.schemas.notification import NotificationCreate, NotificationResponse
from aezakmi_task.services.notification_service import NotificationService
from aezakmi_task.utils.cache import cache
from aezakmi_task.utils.metrics import (
    CREATE_NOTIFICATION_METHOD_DURATION,
    GET_ALL_NOTIFICATIONS_METHOD_DURATION,
    measure_latency,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/notifications/", response_model=NotificationResponse)
@measure_latency(CREATE_NOTIFICATION_METHOD_DURATION)
async def create_notification(
        notification: NotificationCreate,
        service: FromDishka[NotificationService]
):
    db_notification = await service.create_notification(notification)
    await send_new_notification_to_user(
        user_id=str(notification.user_id),
        notification=db_notification
    )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=db_notification.model_dump_json(indent=4)
    )

async def send_new_notification_to_user(user_id: str, notification: NotificationResponse):
    if user_id in websocket_connections:
        for websocket in websocket_connections[user_id]:
            await websocket.send_json(notification.model_dump(mode='json'))


@router.get("/notifications/")
@measure_latency(GET_ALL_NOTIFICATIONS_METHOD_DURATION)
@cache(ttl=10)
async def get_notifications(
        service: FromDishka[NotificationService],
        redis_client: FromDishka[Redis],  # noqa
        user_id: str = None,
        skip: int = 0,
        limit: int = 10,
        status_: str = None,
):
    res = await service.get_notifications(skip=skip, limit=limit, status=status_, user_id=user_id)
    return res


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
@cache(ttl=10)
async def get_notification(
        notification_id: str,
        redis_client: FromDishka[Redis],  # noqa
        service: FromDishka[NotificationService]
):
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.post("/notifications/{notification_id}/mark-as-read", response_model=NotificationResponse)
async def mark_notification_as_read(
        notification_id: str,
        service: FromDishka[NotificationService]
):
    notification = await service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: str = Query(...),
):
    await websocket.accept()
    if user_id not in websocket_connections:
        websocket_connections[user_id] = []
    websocket_connections[user_id].append(websocket)

    try:
        while True:
            # Держим соединение открытым
            await websocket.receive_text()
    except Exception:
        websocket_connections[user_id].remove(websocket)
        if not websocket_connections[user_id]:
            del websocket_connections[user_id]
    finally:
        with suppress(RuntimeError):
            await websocket.close()


websocket_connections = {}
