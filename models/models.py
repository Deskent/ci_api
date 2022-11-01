from datetime import datetime, time
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlmodel import SQLModel, Field, Relationship


class AlarmBase(SQLModel):
    alarm_time: time
    text: Optional[str] = Field(nullable=True, default='')


class AlarmCreate(AlarmBase):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class AlarmUpdate(AlarmCreate):
    pass


class Alarm(AlarmCreate, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True, index=True)
    user: Optional['User'] = Relationship(back_populates="alarms")


class NotificationBase(SQLModel):
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')


class NotificationCreate(NotificationBase):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class NotificationUpdate(NotificationCreate):
    pass


class Notification(NotificationCreate, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    users: List['User'] = Relationship(back_populates="notifications")


class VideoBase(SQLModel):
    path: str
    name: Optional[str] = Field(nullable=True, default='')
    description: Optional[str] = Field(nullable=True, default='')
    previous_id: Optional[int]
    next_id: int


class VideoCreate(VideoBase):
    pass


class Video(VideoBase, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)


class UserCreate(SQLModel):
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)


class UserFullData(SQLModel):
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    current_video: Optional[int] = Field(nullable=True, default=None, foreign_key='videos.id')
    expired_at: Optional[datetime] = Field(default=None)


class UserUpdate(UserFullData):
    username: Optional[str] = Field(unique=True, nullable=False)
    email: Optional[str] = Field(unique=True, nullable=False)
    password: Optional[str] = Field(nullable=False)


class User(UserCreate, UserFullData, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default=datetime.now(tz=None))
    alarms: List[Alarm] = Relationship(back_populates="user")
    notifications: List[Notification] = Relationship(back_populates="users")
