from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field, Relationship, SQLModel


class Complex(SQLModel, table=True):
    __tablename__ = 'complexes'

    id: int = Field(default=None, primary_key=True, index=True)
    number: int = Field(default=None, unique=True, description="Порядковый номер комплекса")
    name: Optional[str] = Field(nullable=True, default='', description="Название комплекса")
    description: Optional[str] = Field(nullable=True, default='', description="Описание комплекса")
    duration: int = Field(nullable=True, default=0, description="Длительность комплекса в секундах")
    video_count: int = Field(nullable=True, default=0, description="Количество видео в комплексе")

    videos: List["Video"] = Relationship(
        back_populates="complexes", sa_relationship_kwargs={"cascade": "delete"})

    viewed_complexes: List['ViewedComplex'] = Relationship(
        back_populates="complexes", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Video(SQLModel, table=True):
    __tablename__ = 'videos'

    id: int = Field(default=None, primary_key=True, index=True)
    file_name: str = Field(nullable=False, description="Путь к файлу видео")
    name: Optional[str] = Field(nullable=True, default='', description="Название видео")
    description: Optional[str] = Field(nullable=True, default='', description="Описание видео")
    duration: int = Field(nullable=True, default=None, description="Длительность видео")
    number: int = Field(default=None, description="Порядковый номер ролика")

    complex_id: Optional[int] = Field(
        default=None, foreign_key="complexes.id",
        description="В каком комплексе")
    complexes: Complex = Relationship(back_populates="videos")

    viewed_videos: List['ViewedVideo'] = Relationship(
        back_populates="videos", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Avatar(SQLModel, table=True):
    __tablename__ = 'avatars'

    id: int = Field(default=None, primary_key=True, index=True)
    file_name: str = Field(nullable=False, description="Имя файла аватарки")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Mood(SQLModel, table=True):
    __tablename__ = 'moods'

    id: int = Field(default=None, primary_key=True, index=True)
    code: Optional[str] = Field(
        nullable=True, default=None, description="HTML код настроения (эмодзи)")
    name: Optional[str] = Field(
        nullable=True, default=None, description="Название настроения (эмодзи)")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, description="Имя")
    last_name: str = Field(nullable=True, default='', description="Фамилия")
    third_name: str = Field(nullable=True, default='', description="Отчество")
    email: EmailStr = Field(unique=True, index=True)
    phone: str = Field(
        unique=True, nullable=False, min_length=10, max_length=13,
        description="Телефон в формате 9998887766")
    password: str = Field(nullable=False, max_length=256, min_length=6, exclude=True)
    gender: bool = Field(nullable=False, description='Пол, 1 - муж, 0 - жен')
    level: int = Field(nullable=False, default=1, description="Текущий уровень")
    progress: int = Field(
        nullable=False, default=0,
        description="Процент прогресса просмотра текущего комплекса")
    created_at: datetime = Field(
        default=datetime.now(tz=None),
        description='Дата создания аккаунта')

    expired_at: Optional[datetime] = Field(
        default=None, description='Дата истечения подписки',
        sa_column=Column(type_=TIMESTAMP(timezone=True)))
    last_entry: Optional[datetime] = Field(
        default=None, description='Дата последнего входа',
        sa_column=Column(type_=TIMESTAMP(timezone=True)))
    is_verified: Optional[bool] = Field(default=False, description='Верифицирован ли телефон')
    is_email_verified: Optional[bool] = Field(default=False, description='Верифицировал ли емэйл')
    is_active: Optional[bool] = Field(default=False, description='Есть ли подписка')
    email_code: Optional[str] = Field(nullable=True, default=None, description="Код верификации")
    sms_message: Optional[str] = Field(nullable=True, default=None, description="Сообщение из смс")
    sms_call_code: Optional[str] = Field(nullable=True, default=None, description="Код из звонка")
    push_token: Optional[str] = Field(
        nullable=True, default=None, description="Токен для пуш-уведомлений")

    mood: int = Field(nullable=True, default=None, foreign_key='moods.id')
    avatar: int = Field(nullable=True, default=None, foreign_key='avatars.id')
    rate_id: int = Field(nullable=False, foreign_key='rates.id')
    current_complex: Optional[int] = Field(nullable=True, default=1, foreign_key='complexes.id')

    alarms: List['Alarm'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    notifications: List['Notification'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    payments: List['Payment'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    payment_checks: List['PaymentCheck'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    viewed_complexes: List['ViewedComplex'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    viewed_videos: List['ViewedVideo'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Rate(SQLModel, table=True):
    __tablename__ = 'rates'

    id: int = Field(default=None, primary_key=True, index=True)
    name: Optional[str] = Field(nullable=True, default='', description="Название тарифа")
    price: int = Field(nullable=False, description="Цена")
    duration: int = Field(nullable=True, default=None, description="Длительность тарифа в секундах")
    payments: List['Payment'] = Relationship(
        back_populates="rates", sa_relationship_kwargs={"cascade": "delete"})
    payment_checks: List['PaymentCheck'] = Relationship(
        back_populates="rates", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Administrator(SQLModel, table=True):
    __tablename__ = 'admins'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, description="Имя")
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(nullable=False, max_length=256, min_length=6, exclude=True)
    name: str = Field(nullable=True, default=None)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Alarm(SQLModel, table=True):
    """Alarm model

    Attributes

        id: int

        alarm_time: time

        sound_name: str

        volume: int

        vibration: bool

        text: Optional[str]

        weekdays: Optional[str]

        user_id: Optional[int]
    """
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
        return f"{self.__class__.__name__}: {self.__dict__}"


class Notification(SQLModel, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    text: Optional[str] = Field(nullable=True, default='', description="Текст уведомления")
    created_at: datetime = Field(default=None, description="Дата создания")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="notifications")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class ViewedComplex(SQLModel, table=True):
    __tablename__ = 'viewed_complexes'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="viewed_complexes")

    viewed_at: datetime = Field(
        default=None, description="Время последнего просмотренного комплекса"
    )

    complex_id: int = Field(nullable=False, foreign_key='complexes.id')
    complexes: 'Complex' = Relationship(back_populates="viewed_complexes")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class ViewedVideo(SQLModel, table=True):
    __tablename__ = 'viewed_videos'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="viewed_videos")

    video_id: int = Field(nullable=False, foreign_key='videos.id')
    videos: 'Video' = Relationship(back_populates="viewed_videos")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class Payment(SQLModel, table=True):
    __tablename__ = 'payments'

    id: int = Field(default=None, primary_key=True, index=True)

    payment_id: int = Field(unique=True)
    payment_sign: str = Field(unique=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="payments")
    rate_id: int = Field(nullable=False, foreign_key='rates.id')
    rates: 'Rate' = Relationship(back_populates="payments")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class PaymentCheck(SQLModel, table=True):
    __tablename__ = 'payment_checks'

    id: int = Field(default=None, primary_key=True, index=True)

    date: datetime = Field(
        description="'date' in Prodamus report",
        sa_column=Column(type_=TIMESTAMP(timezone=True))
    )
    order_id: int = Field(unique=True, description="'order_id' in Prodamus report")

    sum: str = Field(description="'sum' in Prodamus report")
    currency: str = Field(description="'currency' in Prodamus report")
    customer_phone: str = Field(description="'customer_phone' in Prodamus report")
    customer_email: EmailStr = Field(description="'customer_email' in Prodamus report")
    payment_type: str = Field(description="'payment_type' in Prodamus report")
    payment_status: str = Field(description="'payment_status' in Prodamus report")

    user_id: int = Field(
        nullable=False,
        foreign_key='users.id',
        description="Named 'customer_extra' in Prodamus report"
    )
    users: 'User' = Relationship(back_populates="payment_checks")

    rate_id: int = Field(
        nullable=False, foreign_key='rates.id', description="Named 'order_num' in Prodamus report")
    rates: 'Rate' = Relationship(back_populates="payment_checks")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"
