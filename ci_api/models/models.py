from datetime import datetime, time
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.base import MySQLModel, UserModel


class Complex(MySQLModel, table=True):
    __tablename__ = 'complexes'

    id: int = Field(default=None, primary_key=True, index=True)
    number: int = Field(default=None, unique=True, description="Порядковый номер комплекса")
    name: Optional[str] = Field(nullable=True, default='', description="Название комплекса")
    description: Optional[str] = Field(nullable=True, default='', description="Описание комплекса")
    next_complex_id: int = Field(nullable=True, default=1, description="ИД следующего комплекса")
    duration: int = Field(nullable=True, default=0, description="Длительность комплекса в секундах")
    video_count: int = Field(nullable=True, default=0, description="Количество видео в комплексе")

    videos: List["Video"] = Relationship(
        back_populates="complexes", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"№ {self.number}: {self.description}"

    @classmethod
    async def add_new(
            cls: 'Complex',
            session: AsyncSession,
            number: int,
            name: str = '',
            description: str = '',
            duration: int = 0,
            next_complex_id: int = 1,
            video_count: int = 0
    ) -> 'Complex':

        new_complex = Complex(
            number=number, name=name, description=description, next_complex_id=next_complex_id,
            duration=duration, video_count=video_count
        )
        await new_complex.save(session)

        return new_complex


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

    @classmethod
    async def add_new(
            cls: 'Video',
            session: AsyncSession,
            file_name: str,
            complex_id: int,
            duration: int,
            name: str = '',
            description: str = '',
    ) -> 'Video':

        new_video = Video(
            name=name, description=description, complex_id=complex_id,
            duration=duration, file_name=file_name
        )
        await new_video.save(session)
        current_complex = await Complex.get_by_id(session, complex_id)
        current_complex.duration += duration
        current_complex.video_count += 1
        await current_complex.save(session)

        return new_video

    @classmethod
    async def get_videos_duration(cls, session: AsyncSession, videos_ids: tuple[int]):
        query = select(cls).where(cls.id in videos_ids)
        response = await session.execute(query)

        return sum(response.scalars().all())

    async def delete(self, session: AsyncSession) -> None:
        current_complex = await Complex.get_by_id(session, self.complex_id)
        current_complex.video_count -= 1
        await current_complex.save(session)
        await session.delete(self)
        await session.commit()


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
    alarms: List['Alarm'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})
    notifications: List['Notification'] = Relationship(
        back_populates="users", sa_relationship_kwargs={"cascade": "delete"})

    def __str__(self):
        return f"{self.email}"


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


class UserDataModels(MySQLModel):

    @classmethod
    async def get_all_by_user_id(cls, session: AsyncSession, user_id: int) -> list[MySQLModel]:
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


class ViewedComplexes(MySQLModel, table=True):
    __tablename__ = 'viewed_complexes'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    complex_id: int = Field(nullable=False, foreign_key='complexes.id')

    @classmethod
    async def add_viewed(
            cls, session: AsyncSession, user_id: int, complex_id: int
    ) -> 'ViewedComplexes':

        query = select(cls).where(cls.user_id == user_id).where(cls.complex_id == complex_id)
        response = await session.execute(query)
        complex_exists = response.scalars().first()
        if not complex_exists:
            viewed_complex = cls(user_id=user_id, complex_id=complex_id)
            await viewed_complex.save(session)

            return viewed_complex

    @classmethod
    async def get_all_viewed_complexes(
            cls, session: AsyncSession,
            user_id: int
    ) -> list['ViewedComplexes']:

        query = select(cls).where(cls.user_id == user_id)
        viewed_complexes = await session.execute(query)

        return viewed_complexes.scalars().all()


class ViewedVideos(MySQLModel, table=True):
    __tablename__ = 'viewed_videos'

    id: int = Field(default=None, primary_key=True, index=True)

    user_id: int = Field(nullable=False, foreign_key='users.id')
    video_id: int = Field(nullable=False, foreign_key='videos.id')

    @classmethod
    async def add_viewed(cls, session: AsyncSession, user_id: int, video_id: int) -> 'ViewedVideos':
        query = select(cls).where(cls.user_id == user_id).where(cls.video_id == video_id)
        response = await session.execute(query)
        video_exists = response.scalars().first()
        if not video_exists:
            viewed_video = cls(user_id=user_id, video_id=video_id)
            await viewed_video.save(session)

            return viewed_video

    @classmethod
    async def get_all_viewed_videos(
            cls, session: AsyncSession, user_id: int
    ) -> list['ViewedVideos']:

        query = select(cls).where(cls.user_id == user_id)
        viewed_complexes = await session.execute(query)

        return viewed_complexes.scalars().all()
