from datetime import datetime

from pydantic import BaseModel


class NotificationID(BaseModel):
    id: int


class NotificationBase(BaseModel):
    created_at: datetime
    text: str = ''

    def validate_datetime(self):
        self.created_at = self.created_at.replace(tzinfo=None)
        return self


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationID, NotificationBase):
    user_id: int
