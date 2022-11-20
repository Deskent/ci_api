from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class Alarm(SQLModel, table=True):
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
    name: Optional[str] = Field(nullable=True, default='', description="Название комплекса")
    description: Optional[str] = Field(nullable=True, default='', description="Описание комплекса")
    next_complex_id: int = Field(nullable=True, default=1, description="ИД следующего комплекса")
    duration: time = Field(nullable=True, default=None, description="Длительность комплекса")
    video_count: int = Field(nullable=True, default=0, description="Количество видео в комплексе")

    videos: List["Video"] = Relationship(
        back_populates="complexes", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.id}-{self.description}"


class Video(SQLModel, table=True):
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


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False)
    email: EmailStr = Field(unique=True, index=True)
    phone: str = Field(unique=True, nullable=False, min_length=10, max_length=13,
                       description="Телефон в формате 9998887766")
    password: str = Field(nullable=False, max_length=256, min_length=6, exclude=True)
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
    alarms: List[Alarm] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    notifications: List[Notification] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.username}"
