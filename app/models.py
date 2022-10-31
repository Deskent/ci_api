from datetime import datetime, time, timezone
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, Relationship


class BaseSQLModel(SQLModel):
    async def update_data(
            self,
            session: AsyncSession,
            data: SQLModel,
            exclude_unset: bool = True
    ) -> SQLModel:
        data_dict: dict = data.dict(exclude_unset=exclude_unset)
        print(data_dict)

        for key, value in data_dict.items():
            if value:
                setattr(self, key, value)
        session.add(self)
        await session.commit()

        return self


class AlarmBase(BaseSQLModel):
    alarm_time: time
    text: str


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
    text: str


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
    name: str
    description: str
    next_id: int


class Video(VideoBase, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True)


class VideoCreate(VideoBase):
    pass


class UserBase(BaseSQLModel):
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)


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


class UserUpdate(UserFullData):
    pass

