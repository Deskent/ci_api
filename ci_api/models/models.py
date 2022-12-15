from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import Column, TIMESTAMP, desc
from sqlmodel import Field, Relationship, select

from models.methods import MySQLModel, UserModel, get_all, get_first, AdminModel


class Complex(MySQLModel, table=True):
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
        return f"№ {self.number}: {self.description}"

    @classmethod
    async def get_first(cls) -> 'Complex':
        query = select(cls).order_by(cls.number)
        return await get_first(query)

    async def next_complex(self) -> 'Complex':
        query = select(Complex).where(Complex.number == self.number + 1)
        next_complex: Complex = await get_first(query)
        if not next_complex:
            return await Complex.get_first()

        return next_complex

    @classmethod
    async def get_next_complex(cls, complex_id: int) -> 'Complex':
        query = select(cls).where(cls.id == complex_id)
        current_complex: Complex = await get_first(query)

        return await current_complex.next_complex()

    @classmethod
    async def add_new(
            cls: 'Complex',
            number: int,
            name: str = '',
            description: str = '',
            duration: int = 0,
            video_count: int = 0
    ) -> 'Complex':
        new_complex = Complex(
            number=number, name=name, description=description, duration=duration,
            video_count=video_count
        )
        await new_complex.save()

        return new_complex


class Video(MySQLModel, table=True):
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
        return f"{self.name}"

    async def next_video_id(self) -> int:
        query = select(Video).where(Video.number == self.number + 1)
        next_video: Video = await get_first(query)

        return 1 if not next_video else next_video.id

    @classmethod
    async def get_ordered_list(cls, complex_id: int):
        query = select(cls).where(cls.complex_id == complex_id).order_by(cls.number)
        return await get_all(query)

    @classmethod
    async def get_all_by_complex_id(cls, complex_id: int):
        return await cls.get_ordered_list(complex_id)

    @classmethod
    async def add_new(
            cls: 'Video',
            file_name: str,
            complex_id: int,
            duration: int,
            number: int,
            name: str = '',
            description: str = '',
    ) -> 'Video':
        new_video = Video(
            name=name, description=description, complex_id=complex_id,
            duration=duration, file_name=file_name, number=number
        )
        await new_video.save()
        current_complex = await Complex.get_by_id(complex_id)
        current_complex.duration += duration
        current_complex.video_count += 1
        await current_complex.save()

        return new_video

    @classmethod
    async def get_videos_duration(cls, videos_ids: tuple[int]) -> int:
        query = select(cls.duration).where(cls.id.in_(videos_ids))
        durations: list[int] = await get_all(query)

        return sum(durations)

    async def delete(self) -> None:
        current_complex = await Complex.get_by_id(self.complex_id)
        current_complex.video_count -= 1
        await current_complex.save()
        await self.delete()


class Avatar(MySQLModel, table=True):
    __tablename__ = 'avatars'

    id: int = Field(default=None, primary_key=True, index=True)
    file_name: str = Field(nullable=False, description="Имя файла аватарки")

    @classmethod
    async def get_first_id(cls):
        query = select(cls.id).order_by(cls.id)
        return await get_first(query)


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
    expired_at: Optional[datetime] = Field(
        default=None, sa_column=Column(type_=TIMESTAMP(timezone=True))
    )
    is_verified: Optional[bool] = Field(default=False)
    is_email_verified: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    email_code: Optional[str] = Field(nullable=True, default=None, description="Код верификации")
    sms_message: Optional[str] = Field(nullable=True, default=None, description="Сообщение из смс")
    sms_call_code: Optional[str] = Field(nullable=True, default=None, description="Код из звонка")
    push_token: Optional[str] = Field(nullable=True, default=None, description="Токен для пуш-уведомлений")

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
        return f"{self.email}"

    async def level_up(self, next_complex_id: int) -> 'User':
        if self.level < 10:
            self.current_complex = next_complex_id
            self.progress = 0
            self.level += 1
            await self.save()
        return self

    @classmethod
    async def create(cls, data: dict) -> 'User':
        data['password'] = await cls.get_hashed_password(data['password'])
        data['avatar'] = await Avatar.get_first_id()
        user = cls(**data)

        return await user.save()

class Rate(MySQLModel, table=True):
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
        return f"{self.id}: {self.name}"

    @classmethod
    async def get_free(cls) -> 'Rate':
        query = select(cls).where(cls.price == 0)
        return await get_first(query)


class Administrator(AdminModel, table=True):
    __tablename__ = 'admins'

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, description="Имя")
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(nullable=False, max_length=256, min_length=6, exclude=True)
    name: str = Field(nullable=True, default=None)


class Alarm(MySQLModel, table=True):
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

    @classmethod
    async def get_all_by_user_id(cls, user_id: int) -> list[MySQLModel]:
        """Join cls rows with User table where User.id == user_id"""

        query = select(cls).join(User).where(User.id == user_id).order_by(desc(cls.id))

        return await get_all(query)

class Notification(MySQLModel, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True, index=True)
    text: Optional[str] = Field(nullable=True, default='', description="Текст уведомления")
    created_at: datetime = Field(default=None, description="Дата создания")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    users: 'User' = Relationship(back_populates="notifications")

    def __str__(self):
        return f"{self.text}"

    @classmethod
    async def get_all_by_user_id(cls, user_id: int) -> list[MySQLModel]:
        """Join cls rows with User table where User.id == user_id"""

        query = select(cls).join(User).where(User.id == user_id)

        return await get_all(query)


class ViewedComplex(MySQLModel, table=True):
    __tablename__ = 'viewed_complexes'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="viewed_complexes")

    viewed_at: datetime = Field(
        default=None, description="Время последнего просмотренного комплекса"
    )

    complex_id: int = Field(nullable=False, foreign_key='complexes.id')
    complexes: 'Complex' = Relationship(back_populates="viewed_complexes")

    @classmethod
    async def add_viewed(
            cls, user_id: int, complex_id: int
    ) -> 'ViewedComplex':

        query = select(cls).where(cls.user_id == user_id).where(cls.complex_id == complex_id)
        complex_exists = await get_all(query)
        if not complex_exists:
            viewed_complex = cls(
                user_id=user_id, complex_id=complex_id, viewed_at=datetime.now(tz=None)
            )
            await viewed_complex.save()

            return viewed_complex

    @classmethod
    async def get_all_viewed_complexes(
            cls,
            user_id: int
    ) -> list['ViewedComplex']:

        query = select(cls).where(cls.user_id == user_id)
        return await get_all(query)

    @classmethod
    async def is_viewed_complex(
            cls,
            user_id: int,
            complex_id: int
    ) -> 'ViewedComplex':

        query = select(cls).where(cls.user_id == user_id).where(cls.id == complex_id)
        return await get_first(query)

    @classmethod
    async def is_last_viewed_today(cls, user_id: int) -> bool:
        """
        Check Complex viewed today

        True if viewed  else False
        """

        current_day = datetime.now(tz=None).day
        query = select(cls).where(cls.user_id == user_id).order_by(cls.viewed_at)
        last: ViewedComplex = await get_first(query)
        if last and last.viewed_at:
            return current_day == last.viewed_at.day


class ViewedVideo(MySQLModel, table=True):
    __tablename__ = 'viewed_videos'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="viewed_videos")

    video_id: int = Field(nullable=False, foreign_key='videos.id')
    videos: 'Video' = Relationship(back_populates="viewed_videos")

    @classmethod
    async def add_viewed(cls, user_id: int, video_id: int) -> 'ViewedVideo':
        query = select(cls).where(cls.user_id == user_id).where(cls.video_id == video_id)
        video_exists = await get_first(query)
        if not video_exists:
            viewed_video = cls(user_id=user_id, video_id=video_id)
            await viewed_video.save()

            return viewed_video

    @classmethod
    async def get_all_viewed_videos(
            cls, user_id: int
    ) -> list['ViewedVideo']:
        query = select(cls).where(cls.user_id == user_id)

        return await get_all(query)


class Payment(MySQLModel, table=True):
    __tablename__ = 'payments'

    id: int = Field(default=None, primary_key=True, index=True)

    payment_id: int = Field(unique=True)
    payment_sign: str = Field(unique=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    users: 'User' = Relationship(back_populates="payments")
    rate_id: int = Field(nullable=False, foreign_key='rates.id')
    rates: 'Rate' = Relationship(back_populates="payments")

    @classmethod
    async def get_by_user_and_rate_id(cls, user_id: int, rate_id: int) -> 'Payment':
        query = select(cls).where(cls.user_id == user_id).where(cls.rate_id == rate_id)
        result = await get_first(query)
        return result


class PaymentCheck(MySQLModel, table=True):
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

    rate_id: int= Field(
        nullable=False, foreign_key='rates.id', description="Named 'order_num' in Prodamus report"
    )
    rates: 'Rate' = Relationship(back_populates="payment_checks")

    @classmethod
    async def get_all_by_user_id(cls, user_id: int) -> list['PaymentCheck']:
        """Return all rows by user_id"""

        query = select(cls).where(cls.user_id == user_id)
        return await get_all(query)

