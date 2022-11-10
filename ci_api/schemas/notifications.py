from datetime import time

from pydantic import BaseModel


class NotificationID(BaseModel):
    id: int


class NotificationBase(BaseModel):
    notification_time: time
    text: str = ''


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationID, NotificationBase):
    pass
