from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, Relationship


class Alarm(SQLModel, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True, index=True)
    alarm_time: time
    sound_name: str = Field(nullable=True, default='')
    volume: int = Field(nullable=True, default=50)
    vibration: bool = Field(default=False)
    text: Optional[str] = Field(nullable=True, default='')
    weekdays: Optional[str] = Field(nullable=True, default='')

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
    next_complex_id: int = Field(nullable=True, default=1)

    videos: List["Video"] = Relationship(back_populates="complexes")

    def __str__(self):
        return f"{self.id}-{self.description}"


class Video(SQLModel, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)
    path: str = Field(nullable=False, description="Путь к файлу видео")
    name: Optional[str] = Field(nullable=True, default='', description="Название видео")
    description: Optional[str] = Field(nullable=True, default='', description="Описание видео")
    duration: float = Field(nullable=True, default=0, description="Длительность видео")

    complex_id: Optional[int] = Field(
        default=None, foreign_key="complexes.id",
        description="В каком комплексе")
    complexes: Complex = Relationship(back_populates="videos")

    def __str__(self):
        return f"{self.name}"

    @classmethod
    async def get_all_complex_videos(
            cls: 'Video', session: AsyncSession, complex_id: int
    ) -> list['Video']:
        query = select(Video).where(Video.complex_id == complex_id)
        videos_row: Row = await session.execute(query)

        return videos_row.scalars().all()


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    phone: str = Field(unique=True, nullable=False, min_length=10, max_length=13,
                       description="Телефон в формате 9998887766")
    password: str = Field(nullable=False, max_length=256, min_length=6)
    gender: bool = Field(nullable=False, description='Пол, 1 = муж, 0 - жен')
    level: int = Field(nullable=False, default=1, description="Текущий уровень")
    progress: int = Field(nullable=False, default=0,
                          description="Процент прогресса просмотра текущего комплекса")
    created_at: datetime = Field(default=datetime.now(tz=None))
    expired_at: Optional[datetime] = Field(default=None)
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)

    current_complex: Optional[int] = Field(nullable=True, default=1, foreign_key='complexes.id')
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

    @classmethod
    async def get_user_alarms(cls, session: AsyncSession, user_id: int) -> list[Alarm]:
        query = select(Alarm).join(User).where(User.id == user_id)
        alarms = await session.execute(query)

        return alarms.scalars().all()

    @classmethod
    async def get_user_notifications(cls, session: AsyncSession, user_id: int) -> list[Notification]:
        query = select(Notification).join(User).where(User.id == user_id)
        notifications: Row = await session.execute(query)

        return notifications.scalars().all()

