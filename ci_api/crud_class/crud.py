from datetime import datetime, timedelta, timezone

from pydantic import EmailStr
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.engine.result import Result

from config import logger
from database.db import get_db_session
from exc.exceptions import ComplexNotFoundError
from services.auth import auth_handler
# from services.models_cache.base_cache import AllCache
from crud_class.ci_types import *
from services.utils import get_current_datetime
from services.weekdays import WeekDay


async def get_session_response(query) -> Result:
    result = None
    async for session in get_db_session():
        result = await session.execute(query)

    return result


async def get_all(query) -> list:
    result = await get_session_response(query)

    return result.scalars().all()


async def get_first(query):
    result = await get_session_response(query)

    return result.scalars().first()


class BaseCrud:
    def __init__(self, model: MODEL_TYPES, use_cache: bool = True):
        self.model: MODEL_TYPES = model
        self.use_cache: bool = use_cache

    async def save(self, obj: TYPES):
        async for session in get_db_session():
            session.add(obj)
            await session.commit()
        return obj

    async def get_by_id(self, id_: int, use_cache: bool = True) -> MODEL_TYPES:
        # if self.use_cache or use_cache:
        #     result: MODEL_TYPES = await AllCache.get_by_id(self.model, id_)
        #     if result:
        #         return result
        query = select(self.model).where(self.model.id == id_)
        return await get_first(query)

    async def get_all(self, use_cache: bool = True) -> list[MODEL_TYPES]:
        # if self.use_cache or use_cache:
        #     result: list[MODEL_TYPES] = await AllCache.get_all(self.model)
        #     if result:
        #         return result
        query = select(self.model).order_by(self.model.id)
        result: list[MODEL_TYPES] = await get_all(query)
        # await AllCache.update_data(self.model, result)

        return result

    async def delete_by_id(self, id_: int):
        obj: MODEL_TYPES = await self.get_by_id(id_)
        if obj:
            await self.delete(obj)

    @staticmethod
    async def delete(obj: MODEL_TYPES) -> None:
        async for session in get_db_session():
            await session.delete(obj)
            await session.commit()
            logger.debug(f"Object: {obj} deleted")

    async def create(self, data: dict) -> MODEL_TYPES:
        instance = self.model(**data)
        return await instance.save()


class AdminCrud(BaseCrud):
    def __init__(self, model: Type[Administrator | User]):
        super().__init__(model)

    async def get_by_email(self, email: EmailStr) -> User | Administrator:
        query = select(self.model).where(self.model.email == email)
        return await get_first(query)

    async def get_by_token(self, token: str) -> User | Administrator:
        user_id: int = auth_handler.decode_token(token)

        return await self.get_by_id(user_id)

    @staticmethod
    async def get_hashed_password(password: str) -> str:
        return auth_handler.get_password_hash(password)

    @staticmethod
    async def get_user_id_from_email_token(token: str) -> str:
        return auth_handler.decode_token(token)

    @staticmethod
    async def is_password_valid(obj: Type[User | Administrator], password: str) -> bool:
        return auth_handler.verify_password(password, obj.password)

    @staticmethod
    async def get_user_token(obj: Type[User | Administrator]) -> str:
        return auth_handler.encode_token(obj.id)

    async def create(self, data: dict) -> User | Administrator:
        data['password'] = await self.get_hashed_password(data['password'])
        user = self.model(**data)

        return await self.save(user)


class ComplexCrud(BaseCrud):
    def __init__(self, model: Type[Complex]):
        super().__init__(model)

    async def get_first(self) -> Complex:
        query = select(self.model).order_by(self.model.number)
        return await get_first(query)

    async def next_complex(self, obj: Complex) -> Complex:
        query = select(self.model).where(self.model.number == obj.number + 1)
        next_complex: Complex = await get_first(query)
        if not next_complex:
            return await CRUD.complex.get_first()

        return next_complex

    async def get_next_complex_by_id(self, complex_id: int) -> Complex:
        """Return next complex from current complex which got by id"""

        query = select(self.model).where(self.model.id == complex_id)
        current_complex: Complex = await get_first(query)

        return await self.next_complex(current_complex)


class UserCrud(AdminCrud):
    def __init__(self, model: Type[User]):
        super().__init__(model)
        self.user: User | None = None

    async def create(self, data: dict) -> User | Administrator:
        data['password'] = await self.get_hashed_password(data['password'])
        data['avatar'] = await CRUD.avatar.get_first_id()
        user = self.model(**data)

        return await self.save(user)

    async def get_by_phone(self, phone: str) -> User:
        query = select(self.model).where(self.model.phone == phone)
        return await get_first(query)

    async def get_by_email_code(self, email_code: str) -> User:
        query = select(self.model).where(self.model.email_code == email_code)
        return await get_first(query)

    # TODO сделать декоратором
    async def _get_instance(self, user: User = None, id_: int = None) -> User:
        if not user and id_:
            user: User = await self.get_by_id(id_)
        self.user = user
        return self.user

    async def activate(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.is_active = True
            return await self.save(self.user)

    async def deactivate(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.is_active = False
            return await self.save(self.user)

    async def clean_sms_code(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.sms_message = ''
            return await self.save(self.user)

    async def clean_sms_call_code(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.sms_call_code = ''
            return await self.save(self.user)

    async def clean_email_code(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.email_code = ''
            return await self.save(self.user)

    async def set_verified(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.is_verified = True
            return await self.save(self.user)

    async def set_not_verified(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.is_verified = False
            return await self.save(self.user)

    async def level_up(self, user: User = None, id_: int = None) -> User:
        if await self._get_instance(user, id_):
            if self.user.level < 10:
                next_complex: Complex = await CRUD.complex.get_next_complex_by_id(user.current_complex)
                self.user.current_complex = next_complex.id
                self.user.progress = 0
                self.user.level += 1
            return await self.save(self.user)

    @staticmethod
    async def get_alarm_by_alarm_id(user: User, alarm_id: int) -> Alarm:
        """Return user alarm by its id"""

        query = select(Alarm).where(Alarm.user_id == user.id).where(Alarm.id == alarm_id)
        return await get_first(query)

    async def set_subscribe_to(self, days: int, user: User = None,  id_: int = None) -> User:
        if await self._get_instance(user, id_):
            if not user.expired_at or user.expired_at < get_current_datetime():
                user.expired_at = get_current_datetime()
            user.expired_at += timedelta(days=days)
            user.is_active = True
            user.last_entry = get_current_datetime()

            return await self.save(self.user)

    async def set_last_entry_today(self, user: User = None, id_: int = None) -> User:
        """Set last entry user field today value"""

        if await self._get_instance(user, id_):
            user.last_entry = get_current_datetime()
            return await self.save(user)

    async def set_mood(self, mood_id: int, user: User = None,  id_: int = None) -> User:
        if await self._get_instance(user, id_):
            self.user.mood = mood_id
            return await self.save(self.user)

class VideoCrud(BaseCrud):
    def __init__(self, model: Type[Video]):
        super().__init__(model)

    async def next_video_id(self, video: Video) -> int:
        query = select(self.model).where(self.model.number == video.number + 1)
        next_video: Video = await get_first(query)

        return 1 if not next_video else next_video.id

    async def get_ordered_list(self, complex_id: int):
        query = (
            select(self.model)
            .where(self.model.complex_id == complex_id)
            .order_by(self.model.number)
        )
        return await get_all(query)

    async def get_all_by_complex_id(self, complex_id: int):
        return await self.model.get_ordered_list(complex_id)

    async def create(self, data: dict) -> Video:
        """Create new row into DB and add video duration time (seconds)
        to its complex duration"""

        current_complex: Complex = await CRUD.complex.get_by_id(data['complex_id'])
        if not current_complex:
            raise ComplexNotFoundError
        current_complex.duration += data['duration']
        current_complex.video_count += 1
        await self.save(current_complex)

        return await super().create(data)

    async def get_videos_duration(self, videos_ids: tuple[int]) -> int:
        query = select(self.model.duration).where(self.model.id.in_(videos_ids))
        durations: list[int] = await get_all(query)

        return sum(durations)

    async def delete(self, obj: Video) -> None:
        current_complex: Complex = await CRUD.complex.get_by_id(obj.complex_id)
        current_complex.video_count -= 1
        current_complex.duration -= obj.duration
        await self.save(current_complex)
        await self.delete(obj)


class AvatarCrud(BaseCrud):
    def __init__(self, model: Type[Avatar]):
        super().__init__(model)

    async def get_first_id(self) -> int:
        query = select(self.model.id).order_by(self.model.id)
        return await get_first(query)


class RateCrud(BaseCrud):
    def __init__(self, model: Type[Rate]):
        super().__init__(model)

    async def get_free(self) -> Rate:
        query = select(self.model).where(self.model.price == 0)
        return await get_first(query)


class AlarmCrud(BaseCrud):
    def __init__(self, model: Type[Alarm]):
        super().__init__(model)

    async def create(self, data: dict) -> Alarm:
        week_days: WeekDay = WeekDay(data['weekdays'])
        data.update(weekdays=week_days.as_string)

        return await self.save(Alarm(**data))

    async def get_all_by_user_id(self, user_id: int) -> list[Alarm]:
        """Return all user alarms"""

        query = (
            select(self.model).join(User)
            .where(User.id == user_id)
            .order_by(desc(self.model.id))
        )

        return await get_all(query)

    async def for_response(self, obj: Alarm) -> Alarm:
        week_days: WeekDay = WeekDay(obj.weekdays)
        obj.weekdays = week_days.as_list
        obj.alarm_time = obj.alarm_time.strftime("%H:%M")

        return obj


class NotificationCrud(BaseCrud):
    def __init__(self, model: Type[Notification]):
        super().__init__(model)

    async def get_all_by_user_id(self, user_id: int) -> list[Notification]:
        """Return all user notifications"""

        query = select(self.model).join(User).where(User.id == user_id)

        return await get_all(query)


class ViewedComplexCrud(BaseCrud):
    def __init__(self, model: Type[ViewedComplex]):
        super().__init__(model)

    async def add_viewed(self, user_id: int, complex_id: int) -> ViewedComplex:

        query = select(self.model).where(self.model.user_id == user_id).where(self.model.complex_id == complex_id)
        complex_exists = await get_all(query)
        if not complex_exists:
            viewed_complex = self.model(
                user_id=user_id, complex_id=complex_id, viewed_at=get_current_datetime()
            )
            return await self.save(viewed_complex)

    async def get_all_viewed_complexes(self, user_id: int) -> list[ViewedComplex]:
        """Return list of viewed complexes for user"""

        query = select(self.model).where(self.model.user_id == user_id)
        return await get_all(query)

    async def get_all_viewed_complexes_ids(self, user_id: int) -> list[int]:
        """Return list of ids for user"""

        query = select(self.model.id).where(self.model.user_id == user_id)
        return await get_all(query)

    async def is_viewed_complex(self, user_id: int, complex_id: int) -> ViewedComplex:
        """Return ViewedComplex if exists"""

        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.id == complex_id)
        )
        return await get_first(query)

    async def is_last_viewed_today(self, user_id: int) -> bool:
        """
        Check Complex viewed today

        True if viewed  else False
        """

        current_day = get_current_datetime().day
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.viewed_at)
        )
        last: ViewedComplex = await get_first(query)
        if last and last.viewed_at:
            return current_day == last.viewed_at.day


class ViewedVideoCrud(BaseCrud):
    def __init__(self, model: Type[ViewedVideo]):
        super().__init__(model)

    async def add_viewed(self, user_id: int, video_id: int) -> ViewedVideo:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.video_id == video_id)
        )
        video_exists = await get_first(query)
        if not video_exists:
            viewed_video = self.model(user_id=user_id, video_id=video_id)
            return await self.save(viewed_video)

    async def get_all_viewed_videos(self, user_id: int) -> list[ViewedVideo]:
        query = select(self.model).where(self.model.user_id == user_id)

        return await get_all(query)


class PaymentCrud(BaseCrud):
    def __init__(self, model: Type[Payment]):
        super().__init__(model)

    async def get_by_user_and_rate_id(self, user_id: int, rate_id: int) -> Payment:
        query = select(self.model).where(self.model.user_id == user_id).where(self.model.rate_id == rate_id)
        result = await get_first(query)
        return result


class PaymentCheckCrud(BaseCrud):
    def __init__(self, model: Type[PaymentCheck]):
        super().__init__(model)

    async def get_all_by_user_id(self, user_id: int) -> list[PaymentCheck]:
        """Return all rows by user_id"""

        query = select(self.model).where(self.model.user_id == user_id)
        return await get_all(query)


class MoodCrud(BaseCrud):
    def __init__(self, model: Type[Mood]):
        super().__init__(model)


class CRUD:
    user = UserCrud(model=User)
    admin = AdminCrud(model=Administrator)
    complex = ComplexCrud(model=Complex)
    video = VideoCrud(model=Video)
    rate = RateCrud(model=Rate)
    alarm = AlarmCrud(model=Alarm)
    notification = NotificationCrud(model=Notification)
    avatar = AvatarCrud(model=Avatar)
    payment_check = PaymentCheckCrud(model=PaymentCheck)
    payment = PaymentCrud(model=Payment)
    viewed_complex = ViewedComplexCrud(model=ViewedComplex)
    viewed_video = ViewedVideoCrud(model=ViewedVideo)
    mood = MoodCrud(model=Mood)


if __name__ == '__main__':
    a = datetime(2022, 12, 20, 16, 27, 37, 693788, tzinfo=timezone.utc)
    print(a)
    b = datetime.now(tz=timezone.utc)
    print(b)
    print(a < b)
