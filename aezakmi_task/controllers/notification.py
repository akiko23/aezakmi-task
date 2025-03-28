from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from redis.asyncio import Redis
from aezakmi_task.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate
)
from aezakmi_task.services.notification_service import NotificationService
from aezakmi_task.utils.cache import cache

router = APIRouter(route_class=DishkaRoute)


@router.post("/notifications/", response_model=NotificationResponse)
async def create_notification(
        notification: NotificationCreate,
        service: FromDishka[NotificationService]
):
    db_notification = await service.create_notification(notification)
    return Response(status_code=status.HTTP_201_CREATED, content=db_notification.model_dump_json(indent=4))


@router.get("/notifications/")
@cache(ttl=60)
async def get_notifications(
        service: FromDishka[NotificationService],
        redis_client: FromDishka[Redis],  # noqa
        skip: int = 0,
        limit: int = 10,
        status_: str = None,
):
    res = await service.get_notifications(skip=skip, limit=limit, status=status_)
    return res


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
@cache(ttl=60)
async def get_notification(
        notification_id: str,
        redis_client: FromDishka[Redis],  # noqa
        service: FromDishka[NotificationService]
):
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.patch("/notifications/{notification_id}/mark-as-read", response_model=NotificationResponse)
async def mark_notification_as_read(
        notification_id: str,
        service: FromDishka[NotificationService]
):
    notification = await service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification
