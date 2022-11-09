from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, Relationship


class Alarm(SQLModel, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True, index=True)
    alarm_time: time
    text: Optional[str] = Field(nullable=True, default='')
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="alarms")

    def __str__(self):
        return f"{self.text}"


class Notification(SQLModel, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')

    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="notifications")

    def __str__(self):
        return f"{self.text}"


class Complex(SQLModel, table=True):
    __tablename__ = 'complexes'

    id: int = Field(default=None, primary_key=True, index=True)
    description: Optional[str] = Field(nullable=True, default='')

    videos: List["Video"] = Relationship(back_populates="complexes")

    def __str__(self):
        return f"{self.id}-{self.description}"


class Video(SQLModel, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)
    path: str
    name: Optional[str] = Field(nullable=True, default='')
    description: Optional[str] = Field(nullable=True, default='')
    previous_id: Optional[int]
    next_id: Optional[int]

    complex_id: Optional[int] = Field(default=None, foreign_key="complexes.id")
    complexes: Complex = Relationship(back_populates="videos")

    def __str__(self):
        return f"{self.name}"


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    phone: str = Field(unique=True, nullable=False, min_length=10, max_length=13)
    password: str = Field(nullable=False, max_length=256, min_length=6)
    gender: bool = Field(nullable=False, description='Пол, 1 = муж, 0 - жен')
    level: int = Field(nullable=False, default=1)
    progress: float = Field(nullable=False, default=0)
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    expired_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default=datetime.now(tz=None))

    current_complex: Optional[int] = Field(nullable=True, default=1, foreign_key='complexes.id')
    current_video: Optional[int] = Field(nullable=True, default=1, foreign_key='videos.id')
    alarms: List[Alarm] = Relationship(back_populates="users")
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


