from fastapi import APIRouter, HTTPException, status
from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from redis.asyncio import Redis
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate
)
from app.services.notification_service import NotificationService
from app.utils.cache import cache

router = APIRouter(route_class=DishkaRoute)

@router.post("/notifications/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    service: FromDishka[NotificationService]
):
    db_notification = await service.create_notification(notification)
    return db_notification

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
    print("Res:", res)
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

@router.patch("/notifications/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    notification_update: NotificationUpdate,
    service: FromDishka[NotificationService]
):
    notification = await service.update_notification(notification_id, notification_update)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification