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


class Alarm(AlarmCreate, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True)
    users: List['User'] = Relationship(back_populates="alarms")


class AlarmUpdate(AlarmCreate):
    pass


class NotificationBase(SQLModel):
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')


class NotificationCreate(NotificationBase):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class Notification(NotificationCreate, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True)
    users: List['User'] = Relationship(back_populates="notifications")


class NotificationUpdate(NotificationCreate):
    pass


class VideoBase(SQLModel):
    path: str
    name: Optional[str] = Field(nullable=True, default='')
    description: Optional[str] = Field(nullable=True, default='')
    next_id: int


class Video(VideoBase, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True)


class VideoCreate(VideoBase):
    pass


class UserBase(SQLModel):
    username: Optional[str] = Field(unique=True, nullable=False)
    email: Optional[str] = Field(unique=True, nullable=False)
    password: Optional[str] = Field(nullable=False)


class UserFullData(UserBase):
    expired_at: Optional[datetime] = Field(default=None)
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    current_video: Optional[int] = Field(nullable=True, default=None, foreign_key='videos.id')


class User(UserFullData, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(tz=None))
    alarms: List[Alarm] = Relationship(back_populates="users")
    notifications: List[Notification] = Relationship(back_populates="users")


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    expired_at: Optional[datetime] = Field(default=None)
    is_admin: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    current_video: Optional[int] = Field(nullable=True, default=None, foreign_key='videos.id')
