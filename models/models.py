from datetime import datetime, time
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlmodel import SQLModel, Field, Relationship


class BaseSQLModel(SQLModel):
    async def update_data(
            self,
            session: AsyncSession,
            data: SQLModel,
            pk: int,
    ) -> SQLModel:

        new_data = {
            key: value
            for key, value in data.dict().items()
            if value is not None
        }
        if new_data.get('expired_at'):
            new_data['expired_at'] = new_data['expired_at'].replace(tzinfo=None)

        await session.execute(update(User).where(User.id == pk).values(**new_data))

        return self


class AlarmBase(BaseSQLModel):
    alarm_time: time
    text: Optional[str] = Field(nullable=True, default='')


class AlarmCreate(AlarmBase):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class Alarm(AlarmCreate, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True)
    users: List['User'] = Relationship(back_populates="alarms")


class AlarmUpdate(AlarmBase):
    pass


class NotificationBase(BaseSQLModel):
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')


class NotificationCreate(NotificationBase):
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class Notification(NotificationCreate, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True)
    users: List['User'] = Relationship(back_populates="notifications")


class NotificationUpdate(NotificationBase):
    pass


class VideoBase(BaseSQLModel):
    path: str
    name: Optional[str] = Field(nullable=True, default='')
    description: Optional[str] = Field(nullable=True, default='')
    next_id: int


class Video(VideoBase, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True)


class VideoCreate(VideoBase):
    pass


class UserBase(BaseSQLModel):
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

    id: int = Field(default=None, primary_key=True, exclude=True)
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
