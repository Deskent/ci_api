from datetime import datetime, timedelta

from loguru import logger
from pydantic import EmailStr
from sqlalchemy import desc
from sqlalchemy.sql import extract
from sqlmodel import select

from config import get_redis_client
from crud_class.ci_types import *
from crud_class.ci_types import MODEL_TYPES
from database.db import get_all, get_first, get_db_session
from database.models import Administrator, User, Complex, Alarm, Notification, ViewedComplex, Video
from exc.exceptions import ComplexNotFoundError
from misc.weekdays_class import WeekDay
from services.auth import auth_handler
from services.utils import get_current_datetime
from misc.redis_class import RedisDB

USE_CACHE: bool = True


class BaseCrud:
    def __init__(self, model: MODEL_TYPES):
        self.model: MODEL_TYPES = model
        self.redis_db = RedisDB(model=self.model, client=get_redis_client())

    async def save(self, obj: MODEL_TYPES, use_cache: bool = USE_CACHE):
        """Save model instance to DB and to redis """

        async for session in get_db_session():
            session.add(obj)
            await session.commit()

        await self.redis_db.save_by_id(id_=obj.id, data=obj)
        return obj

    async def get_by_id(self, id_: int, use_cache: bool = USE_CACHE) -> MODEL_TYPES:
        """Return one record from redis if exists, else get from DB,
        save to redis and return"""

        if use_cache:
            result: MODEL_TYPES = await self.redis_db.get_by_id(id_=id_)
            if result:
                return result
        query = select(self.model).where(self.model.id == id_)
        result = await get_first(query)
        if result:
            await self.redis_db.save_by_id(id_=result.id, data=result)
            return result

    async def get_all(self, use_cache: bool = USE_CACHE) -> list[MODEL_TYPES]:
        """Return all ordered by id records from redis if exists, else get all records,
        save them to redis and return"""

        if use_cache:
            all_elems: list[MODEL_TYPES] = await self.redis_db.load_all()
            if all_elems:
                return all_elems

        query = select(self.model).order_by(self.model.id)
        result: list[MODEL_TYPES] = await get_all(query)
        await self.redis_db.save_all(result)

        return result

    async def delete_by_id(self, id_: int, use_cache: bool = USE_CACHE):
        """Delete records by id"""

        obj: MODEL_TYPES = await self.get_by_id(id_)
        if obj:
            await self.delete(obj)

    async def _delete_from_redis(self):
        """Delete all records from redis"""

        await self.redis_db.delete_all()

    @staticmethod
    async def delete(obj: MODEL_TYPES) -> None:
        """Delete object from DB"""

        async for session in get_db_session():
            await session.delete(obj)
            await session.commit()
            logger.debug(f"Object: {obj} deleted")

    async def create(self, data: dict) -> MODEL_TYPES:
        """Create and save instance from data"""

        instance = self.model(**data)
        return await self.save(instance)


class AvatarCrud(BaseCrud):
    def __init__(self, model: Type[Avatar]):
        super().__init__(model)

    async def get_first_id(self) -> int:
        """Return first avatar"""
        query = select(self.model.id).order_by(self.model.id)
        return await get_first(query)


class RateCrud(BaseCrud):
    def __init__(self, model: Type[Rate]):
        super().__init__(model)

    async def get_free(self) -> Rate:
        """Return Free rate"""

        query = select(self.model).where(self.model.price == 0)
        return await get_first(query)


class AlarmCrud(BaseCrud):
    def __init__(self, model: Type[Alarm]):
        super().__init__(model)

    async def create(self, data: dict) -> Alarm:
        """Reformat weekdays from list to string and save"""

        week_days: WeekDay = WeekDay(data['weekdays'])
        data.update(weekdays=week_days.as_string)

        return await self.save(Alarm(**data))

    async def get_all_by_user_id(self, user_id: int) -> list[Alarm]:
        """Return all user alarms"""

        query = (
            select(self.model)
            .join(User)
            .where(User.id == user_id)
            .order_by(desc(self.model.id))
        )

        return await get_all(query)

    @staticmethod
    async def for_response(obj: Alarm) -> Alarm:
        """Replace weekdays from digit (index) format [01234] to text
        format ['sunday', 'monday']
        Remove seconds from alarm_time
        """

        week_days: WeekDay = WeekDay(obj.weekdays)
        obj.weekdays = week_days.as_list
        obj.alarm_time = obj.alarm_time.strftime("%H:%M")

        return obj

    async def get_all_active_alarms(self) -> list[Alarm]:
        """Return alarms for active and verified users"""

        query = (
            select(self.model)
            .join(User)
            .where(
                User.is_active
                & User.is_verified
            )
        )

        return await get_all(query)


class NotificationCrud(BaseCrud):
    def __init__(self, model: Type[Notification]):
        super().__init__(model)

    async def get_all_by_user_id(self, user_id: int) -> list[Notification]:
        """Return all user notifications"""

        query = select(self.model).join(User).where(User.id == user_id)

        return await get_all(query)

    @staticmethod
    async def create_and_update_notifications(notifications: list[Notification]) -> None:
        """Add notifications to database"""

        async for session in get_db_session():
            session.add_all(notifications)
            await session.commit()


class ViewedComplexCrud(BaseCrud):
    def __init__(self, model: Type[ViewedComplex]):
        super().__init__(model)

    async def add_viewed(self, user_id: int, complex_id: int) -> ViewedComplex:
        """Add viewed complex to DB if not exists"""

        query = (
            select(self.model)
            .where(
                (self.model.user_id == user_id)
                & (self.model.complex_id == complex_id)
            )
        )
        complex_exists = await get_all(query)
        if not complex_exists:
            viewed_complex = self.model(
                user_id=user_id, complex_id=complex_id, viewed_at=datetime.now(tz=None)
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
            .where(
                (self.model.user_id == user_id)
                & (self.model.id == complex_id)
            )
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
        """Add viewed video to DB if not exists"""

        query = (
            select(self.model)
            .where(
                (self.model.user_id == user_id)
                & (self.model.video_id == video_id)
            )
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
        """Return payment instance for user using rate_id"""

        query = (
            select(self.model)
            .where(
                (self.model.user_id == user_id)
                & (self.model.rate_id == rate_id)
            )
        )
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

    @staticmethod
    async def _replace_code(elem: Mood):
        if 'U+' in elem.code:
            elem.code = elem.code.replace('U+', '0x')

        return elem

    async def create(self, data: dict) -> Mood:
        """Replace U+ to 0x in code if exists"""

        if 'U+' in data['code']:
            data['code'] = data['code'].replace('U+', '0x')

        return await super().create(data)

    async def get_by_id(self, id_: int, *args, **kwargs) -> Mood:
        """Return instance with replaced U+ to 0x code"""

        elem: Mood = await super().get_by_id(id_, *args, **kwargs)

        return await self._replace_code(elem)

    async def get_all(self, *args, **kwargs) -> list[Mood]:
        """Return all instances with replaced U+ to 0x in them code"""

        all_elems: list[Mood] = await super().get_all(*args, **kwargs)
        for elem in all_elems:
            if 'U+' in elem.code:
                elem.code = await self._replace_code(elem)

        return all_elems


class ComplexCrud(BaseCrud):
    def __init__(self, model: Type[Complex]):
        super().__init__(model)

    async def get_first(self) -> Complex:
        """Return start complex id"""

        query = select(self.model).order_by(self.model.number)
        return await get_first(query)

    async def next_complex(self, obj: Complex) -> Complex:
        """Return next complex for current complex instance"""

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


class VideoCrud(BaseCrud):
    def __init__(self, model: Type[Video]):
        super().__init__(model)

    async def next_video_id(self, video: Video) -> int:
        """Return next video for current video"""

        query = select(self.model).where(self.model.number == video.number + 1)
        next_video: Video = await get_first(query)

        return 1 if not next_video else next_video.id

    async def get_ordered_list(self, complex_id: int) -> list[Video]:
        """Return ordered list of videos for complex with current_id"""

        query = (
            select(self.model)
            .where(self.model.complex_id == complex_id)
            .order_by(self.model.number)
        )
        return await get_all(query)

    async def get_all_by_complex_id(self, complex_id: int) -> list[Video]:
        """Return ordered list of videos for complex with current_id"""

        return await self.get_ordered_list(complex_id)

    async def create(self, data: dict) -> Video:
        """Create new row into DB and add video duration time (seconds)
        to its complex duration"""

        complex_id: int = data.get('complex_id')
        if complex_id:
            current_complex: Complex = await CRUD.complex.get_by_id(complex_id)
            if not current_complex:
                raise ComplexNotFoundError
            current_complex.duration += data['duration']
            current_complex.video_count += 1
            await self.save(current_complex)

        return await super().create(data)

    async def get_videos_duration(self, videos_ids: tuple[int]) -> int:
        """Return summary duration for videos with ids from videos_ids"""

        query = select(self.model.duration).where(self.model.id.in_(videos_ids))
        durations: list[int] = await get_all(query)

        return sum(durations)

    async def delete(self, obj: Video) -> None:
        """Reduce complex counter and duration before delete video"""

        current_complex: Complex = await CRUD.complex.get_by_id(obj.complex_id)
        current_complex.video_count -= 1
        current_complex.duration -= obj.duration
        await self.save(current_complex)
        await super().delete(obj)

    async def get_hello_video(self) -> Video:
        """Return hello video instance"""

        query = select(self.model).where(self.model.complex_id.is_(None))
        return await get_first(query)


class AdminCrud(BaseCrud):
    def __init__(self, model: Type[Administrator | User]):
        super().__init__(model)

    async def get_by_email(self, email: EmailStr) -> User | Administrator:
        """Return user instance using email"""

        query = select(self.model).where(self.model.email == email)
        return await get_first(query)

    async def get_by_token(self, token: str) -> User | Administrator:
        """Return user instance using auth token"""

        user_id: int = auth_handler.decode_token(token)

        return await self.get_by_id(user_id)

    @staticmethod
    async def get_hashed_password(password: str) -> str:
        """Return hashed password"""

        return auth_handler.get_password_hash(password)

    @staticmethod
    async def get_user_id_from_email_token(token: str) -> str:
        """Return user instance using email sent token"""

        return auth_handler.decode_token(token)

    @staticmethod
    async def is_password_valid(obj: Type[User | Administrator], password: str) -> bool:
        """Checks passwords equal"""

        return auth_handler.verify_password(password, obj.password)

    @staticmethod
    async def get_user_token(obj: Type[User | Administrator]) -> str:
        """Return user auth token"""

        return auth_handler.encode_token(obj.id)

    async def create(self, data: dict) -> User | Administrator:
        """Create user with hashed password. Return user instance"""

        data['password'] = await self.get_hashed_password(data['password'])

        return await super().create(data)


class UserCrud(AdminCrud):
    def __init__(self, model: Type[User]):
        super().__init__(model)
        self.user: User | None = None

    async def _get_instance(self, user: User = None, id_: int = None) -> User:
        if not user and id_:
            user: User = await self.get_by_id(id_)
        self.user = user
        return self.user

    async def create(self, data: dict) -> User:
        """Create user with hashed password and default avatar. Return user instance"""

        data['password'] = await self.get_hashed_password(data['password'])
        data['avatar'] = await CRUD.avatar.get_first_id()
        user = self.model(**data)

        return await self.save(user)

    async def get_by_phone(self, phone: str) -> User:
        """Return user instance using user phone"""

        query = select(self.model).where(self.model.phone == phone)
        return await get_first(query)

    async def get_by_email_code(self, email_code: str) -> User:
        """Return user instance using user email_code"""

        query = select(self.model).where(self.model.email_code == email_code)
        return await get_first(query)

    async def activate(self, user: User = None, id_: int = None) -> User:
        """Set user is active"""

        if await self._get_instance(user, id_):
            self.user.is_active = True
            return await self.save(self.user)

    async def deactivate(self, user: User = None, id_: int = None) -> User:
        """Set user is not active"""

        if await self._get_instance(user, id_):
            self.user.is_active = False
            return await self.save(self.user)

    async def clean_sms_code(self, user: User = None, id_: int = None) -> User:
        """Clean user sms_code"""

        if await self._get_instance(user, id_):
            self.user.sms_message = ''
            return await self.save(self.user)

    async def clean_sms_call_code(self, user: User = None, id_: int = None) -> User:
        """Clean user call_code"""

        if await self._get_instance(user, id_):
            self.user.sms_call_code = ''
            return await self.save(self.user)

    async def clean_email_code(self, user: User = None, id_: int = None) -> User:
        """Clean user email_code"""

        if await self._get_instance(user, id_):
            self.user.email_code = ''
            return await self.save(self.user)

    async def set_verified(self, user: User = None, id_: int = None) -> User:
        """Set user is verified"""

        if await self._get_instance(user, id_):
            self.user.is_verified = True
            return await self.save(self.user)

    async def set_not_verified(self, user: User = None, id_: int = None) -> User:
        """Set user is not verified"""

        if await self._get_instance(user, id_):
            self.user.is_verified = False
            return await self.save(self.user)

    async def level_up(self, user: User = None, id_: int = None) -> User:
        """Set up user level, next complex and clean progress scale"""
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

    async def set_subscribe_to(self, days: int, user: User = None, id_: int = None) -> User:
        """Set user subcribe, is active and expired data"""
        if await self._get_instance(user, id_):
            if not user.expired_at or await self.check_is_active(self.user):
                user.expired_at = get_current_datetime()
            user.expired_at += timedelta(days=days)
            user.is_active = True

            return await self.save(self.user)

    async def set_last_entry_today(self, user: User = None, id_: int = None) -> User:
        """Set last entry user field today value"""

        if await self._get_instance(user, id_):
            user.last_entry = get_current_datetime()
            return await self.save(user)

    async def set_mood(self, mood_id: int, user: User = None, id_: int = None) -> User:
        """Set user mood"""

        if await self._get_instance(user, id_):
            self.user.mood = mood_id
            return await self.save(self.user)

    async def set_avatar(self, avatar_id: int, user: User = None, id_: int = None) -> User:
        """Set user avatar"""

        if await self._get_instance(user, id_):
            self.user.avatar = avatar_id
            return await self.save(self.user)

    async def check_is_active(self, user: User = None, id_: int = None) -> bool:
        """Check is user have active subscribe. Set False if expired."""

        if await self._get_instance(user, id_):
            if user.expired_at and user.expired_at.date() < get_current_datetime().date():
                user.is_active = False
                user: User = await self.save(user)
            return user.is_active

    async def is_first_entry_today(self, user: User = None, id_: int = None) -> bool:
        """Return True if it first user entry today else False"""

        if await self._get_instance(user, id_):
            if self.user.last_entry is None:
                return True
            return self.user.last_entry.date() != get_current_datetime().date()

    async def is_new_user(self, user: User = None, id_: int = None) -> bool:
        """Check is user new"""

        if await self._get_instance(user, id_):
            return self.user.last_entry is None

    async def get_tokens_for_send_notification_push(self) -> list[str]:
        """Return list of user tokens user having notification"""

        query = (
            select(self.model.push_token)
            .join(Notification)
            .where(self.model.push_token.is_not(None))
        )

        return await get_all(query)

    async def get_users_ids_for_create_notifications(self) -> list[int]:
        """Return users IDs list for sending notifications"""

        today: datetime = datetime.today()
        query = (
            select(self.model.id)
            .where(
                self.model.is_verified
                & self.model.is_active
                & self.model.id.not_in(
                        select(ViewedComplex.user_id)
                        .where(
                            (extract('day', ViewedComplex.viewed_at) == today.day)
                            & (extract('month', ViewedComplex.viewed_at) == today.month)
                            & (extract('year', ViewedComplex.viewed_at) == today.year)
                        )
                )
            )
        )

        return await get_all(query)

    async def get_users_have_notification(
            self,
            users_ids_for_notificate: list[int]
    ) -> list[int]:
        """Return user IDs list who need to create or update notifications"""

        query = (
            select(self.model.id)
            .join(Notification)
            .where(Notification.user_id.in_(users_ids_for_notificate))
        )
        return await get_all(query)


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

    @classmethod
    async def initialize(cls):
        """Delete all data from redis for next models:
            Rate, Avatar, Mood, Video, Complex
        Load DB data for next models:
            Rate, Avatar, Mood, Video, Complex
        """

        await CRUD.rate._delete_from_redis()
        await CRUD.rate.get_all(use_cache=False)
        await CRUD.avatar._delete_from_redis()
        await CRUD.avatar.get_all(use_cache=False)
        await CRUD.mood._delete_from_redis()
        await CRUD.mood.get_all(use_cache=False)
        await CRUD.video._delete_from_redis()
        await CRUD.video.get_all(use_cache=False)
        await CRUD.complex._delete_from_redis()
        await CRUD.complex.get_all(use_cache=False)
