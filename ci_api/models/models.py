from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr, validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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

    def __str__(self):
        return f"{self.text}"

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

    def __str__(self):
        return f"{self.text}"


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

    def __str__(self):
        return f"{self.name}"


class UserCreate(SQLModel):
    username: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(nullable=False, max_length=256, min_length=6)


class UserInput(UserCreate):
    password2: str

    @validator('password2')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords don\'t match')
        return v


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserFullData(SQLModel):
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    current_video: Optional[int] = Field(nullable=True, default=None, foreign_key='videos.id')
    expired_at: Optional[datetime] = Field(default=None)


class UserUpdate(UserFullData):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class UserOutput(UserFullData):
    username: Optional[str]
    email: Optional[EmailStr]


class User(UserCreate, UserFullData, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default=datetime.now(tz=None))
    alarms: List[Alarm] = Relationship(back_populates="user")
    notifications: List[Notification] = Relationship(back_populates="users")

    def __str__(self):
        return f"{self.username}"

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int) -> 'User':
        query = select(cls).where(cls.id == user_id)
        user = await session.execute(query)

        return user.scalars().first()

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: EmailStr) -> 'User':
        query = select(cls).where(cls.email == email)
        user = await session.execute(query)

        return user.scalars().first()
