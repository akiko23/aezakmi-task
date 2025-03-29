from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict


class NotificationBase(BaseModel):
    title: str
    text: str

class NotificationCreate(NotificationBase):
    user_id: UUID4

class NotificationUpdate(BaseModel):
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    created_at: datetime
    read_at: Optional[datetime]
    category: Optional[str]
    confidence: Optional[float]
    processing_status: str


class ManyNotificationsResponse(BaseModel):
    total: int
    results: list[NotificationResponse]
