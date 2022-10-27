from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Column, Text, DateTime, Time, ForeignKey, Boolean
from sqlalchemy.orm import relationship


from sqlmodel import SQLModel, Field, Relationship


class AlertBase(SQLModel):
    time: datetime
    description: str


class Alert(AlertBase, table=True):
    __tablename__ = 'alerts'
    id: int = Field(default=None, primary_key=True)


class AlertCreate(AlertBase):
    pass


class NotificationBase(SQLModel):
    time: datetime
    description: str


class Notification(NotificationBase, table=True):
    __tablename__ = 'notifications'
    id: int = Field(default=None, primary_key=True)


class NotificationCreate(NotificationBase):
    pass


class VideoBase(SQLModel):
    filename: str
    description: str
    #     user = Column(Integer, ForeignKey("users.id"))


class Video(VideoBase, table=True):
    __tablename__ = 'videos'
    id: int = Field(default=None, primary_key=True)


class VideoCreate(VideoBase):
    pass


class UserBase(SQLModel):
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)
    created_at: datetime = Field(nullable=False, default=datetime.utcnow())
    expired_at: datetime = Field(nullable=False, default=datetime.utcnow())
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=False)
    alerts: list[Alert] = Relationship(back_populates="users")
    notifications: list[Notification] = Relationship(back_populates="users")
    current_video: Optional[Video] = Relationship(back_populates="users")


class User(UserBase, table=True):
    __tablename__ = 'users'
    id: int = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass
