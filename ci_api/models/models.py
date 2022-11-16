from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlmodel import SQLModel, Field, Relationship

from database.db import get_session


class BaseSQLModel(SQLModel):

    @classmethod
    async def _exec_in_session(cls, query):
        async for session in get_session():
            return await session.execute(query)

    async def save(self, session=None):
        if session:
            session.add(self)
            await session.commit()
        else:
            async for session in get_session():
                session.add(self)
                await session.commit()
        return self

    @classmethod
    async def get_by_id(cls, id: int):
        async for session in get_session():
            return await session.get(cls, id)


class Alarm(BaseSQLModel, table=True):
    __tablename__ = 'alarms'

    id: int = Field(default=None, primary_key=True, index=True)
    alarm_time: time
    sound_name: str = Field(nullable=False, default='some sound')
    volume: int = Field(nullable=False, default=50)
    vibration: bool = Field(default=False)
    text: Optional[str] = Field(nullable=True, default='')
    weekdays: Optional[str] = Field(nullable=False, default='all')

    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="alarms")

    def __str__(self):
        return f"{self.text}"


class Notification(BaseSQLModel, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')

    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="notifications")

    def __str__(self):
        return f"{self.text}"


class Complex(BaseSQLModel, table=True):
    __tablename__ = 'complexes'

    id: int = Field(default=None, primary_key=True, index=True)
    name: Optional[str] = Field(nullable=True, default='', description="Название комплекса")
    description: Optional[str] = Field(nullable=True, default='', description="Описание комплекса")
    next_complex_id: int = Field(nullable=True, default=1, description="ИД следующего комплекса")
    duration: time = Field(nullable=True, default=None, description="Длительность комплекса")
    video_count: int = Field(nullable=True, default=0, description="Количество видео в комплексе")

    videos: List["Video"] = Relationship(back_populates="complexes")

    def __str__(self):
        return f"{self.id}-{self.description}"


class Video(BaseSQLModel, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)
    file_name: str = Field(nullable=False, description="Путь к файлу видео")
    name: Optional[str] = Field(nullable=True, default='', description="Название видео")
    description: Optional[str] = Field(nullable=True, default='', description="Описание видео")
    duration: time = Field(nullable=True, default=None, description="Длительность видео")

    complex_id: Optional[int] = Field(
        default=None, foreign_key="complexes.id",
        description="В каком комплексе")
    complexes: Complex = Relationship(back_populates="videos")

    def __str__(self):
        return f"{self.name}"

    @classmethod
    async def get_all_complex_videos(cls: 'Video', complex_id: int) -> list['Video']:
        query = select(Video).where(Video.complex_id == complex_id)
        videos_row = await cls._exec_in_session(query)

        return videos_row.scalars().all()


class User(BaseSQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    phone: str = Field(unique=True, nullable=False, min_length=10, max_length=13,
                       description="Телефон в формате 9998887766")
    password: str = Field(nullable=False, max_length=256, min_length=6)
    gender: bool = Field(nullable=False, description='Пол, 1 - муж, 0 - жен')
    level: int = Field(nullable=False, default=1, description="Текущий уровень")
    progress: int = Field(nullable=False, default=0,
                          description="Процент прогресса просмотра текущего комплекса")
    created_at: datetime = Field(default=datetime.now(tz=None))
    expired_at: Optional[datetime] = Field(default=None)
    is_verified: Optional[bool] = Field(default=False)
    is_admin: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)

    current_complex: Optional[int] = Field(nullable=True, default=1, foreign_key='complexes.id')
    alarms: List[Alarm] = Relationship(back_populates="users")
    notifications: List[Notification] = Relationship(back_populates="users")

    def __str__(self):
        return f"{self.username}"

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> 'User':
        query = select(cls).where(cls.id == user_id)
        user = await cls._exec_in_session(query)

        return user.scalars().first()

    @classmethod
    async def get_user_by_email(cls, email: EmailStr) -> 'User':
        query = select(cls).where(cls.email == email)
        user = await cls._exec_in_session(query)

        return user.scalars().first()

    @classmethod
    async def get_user_alarms(cls, user_id: int) -> list[Alarm]:
        query = select(Alarm).join(User).where(User.id == user_id)
        alarms = await cls._exec_in_session(query)

        return alarms.scalars().all()

    @classmethod
    async def get_user_notifications(cls, user_id: int) -> list[Notification]:
        query = select(Notification).join(User).where(User.id == user_id)
        notifications: Row = await cls._exec_in_session(query)

        return notifications.scalars().all()


