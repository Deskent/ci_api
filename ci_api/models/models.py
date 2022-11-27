from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession

from services.auth import auth_handler


class MySQLModel(SQLModel):

    async def save(self, session) -> None:
        session.add(self)
        await session.commit()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id_: int):
        return await session.get(cls, id_)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list:
        response = await session.execute(select(cls))

        return response.scalars().all()

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()


class UserDataModels(MySQLModel):

    @classmethod
    async def get_all_by_user_id(cls, session: AsyncSession, user_id: int):
        query = select(cls).join(User).where(User.id == user_id)
        response = await session.execute(query)

        return response.scalars().all()


class Alarm(UserDataModels, table=True):
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


class Notification(UserDataModels, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    notification_time: time
    text: Optional[str] = Field(nullable=True, default='')

    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="notifications")

    def __str__(self):
        return f"{self.text}"


class Complex(MySQLModel, table=True):
    __tablename__ = 'complexes'

    id: int = Field(default=None, primary_key=True, index=True)
    name: Optional[str] = Field(nullable=True, default='', description="Название комплекса")
    description: Optional[str] = Field(nullable=True, default='', description="Описание комплекса")
    next_complex_id: int = Field(nullable=True, default=1, description="ИД следующего комплекса")
    duration: int = Field(nullable=True, default=None, description="Длительность комплекса")
    video_count: int = Field(nullable=True, default=0, description="Количество видео в комплексе")

    videos: List["Video"] = Relationship(
        back_populates="complexes", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.id}-{self.description}"


class Video(MySQLModel, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)
    file_name: str = Field(nullable=False, description="Путь к файлу видео")
    name: Optional[str] = Field(nullable=True, default='', description="Название видео")
    description: Optional[str] = Field(nullable=True, default='', description="Описание видео")
    duration: int = Field(nullable=True, default=None, description="Длительность видео")

    complex_id: Optional[int] = Field(
        default=None, foreign_key="complexes.id",
        description="В каком комплексе")
    complexes: Complex = Relationship(back_populates="videos")

    def __str__(self):
        return f"{self.name}"

    @classmethod
    async def get_all_by_complex_id(cls, session: AsyncSession, complex_id: int):
        query = select(cls).where(cls.complex_id == complex_id)
        videos_row = await session.execute(query)

        return videos_row.scalars().all()


class UserModel(MySQLModel):

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: EmailStr) -> 'UserModel':
        query = select(cls).where(cls.email == email)
        response = await session.execute(query)

        return response.scalars().first()

    @classmethod
    async def get_by_phone(cls, session: AsyncSession, phone: str) -> 'UserModel':
        query = select(cls).where(cls.phone == phone)
        response = await session.execute(query)

        return response.scalars().first()

    @classmethod
    async def get_by_token(cls, session: AsyncSession, token: str) -> 'UserModel':
        user_id: int = auth_handler.decode_token(token)

        return await session.get(cls, user_id)

    async def is_password_valid(self, password: str) -> bool:
        return auth_handler.verify_password(password, self.password)

    async def get_user_token(self) -> str:
        return auth_handler.encode_token(self.id)

    @staticmethod
    async def get_hashed_password(password: str) -> str:
        return auth_handler.get_password_hash(password)

    @staticmethod
    async def get_user_id_from_email_token(token: str) -> str:
        return auth_handler.decode_token(token)


class User(UserModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, description="Имя")
    last_name: str = Field(nullable=True, default='', description="Фамилия")
    third_name: str = Field(nullable=True, default='', description="Отчество")
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
    is_active: Optional[bool] = Field(default=False)
    sms_message: Optional[str] = Field(nullable=True, default=None, description="Сообщение из смс")
    sms_call_code: Optional[str] = Field(nullable=True, default=None, description="Код из звонка")

    rate_id: int = Field(nullable=False, foreign_key='rates.id')
    current_complex: Optional[int] = Field(nullable=True, default=1, foreign_key='complexes.id')
    alarms: List[Alarm] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    notifications: List[Notification] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.username}"


class Rate(MySQLModel, table=True):
    __tablename__ = 'rates'

    id: int = Field(default=None, primary_key=True, index=True)
    name: Optional[str] = Field(nullable=True, default='', description="Название тарифа")
    price: int = Field(nullable=False, description="Цена")
    duration: int = Field(nullable=True, default=None, description="Длительность тарифа в секундах")

    def __str__(self):
        return f"{self.id}: {self.name}"


class Administrator(UserModel, table=True):
    __tablename__ = 'admins'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, description="Имя")
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(nullable=False, max_length=256, min_length=6, exclude=True)
    name: str = Field(nullable=True, default=None)
