from datetime import time

from pydantic import BaseModel


class NotificationBase(BaseModel):
    notification_time: time
    text: str = ''


class NotificationCreate(NotificationBase):
    user_id: int = None


class NotificationUpdate(NotificationCreate):
    pass
