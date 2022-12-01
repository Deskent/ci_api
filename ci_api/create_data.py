import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from admin.utils import create_default_admin
from config import logger, settings
from database.db import drop_db, create_db, get_db_session
from models.models import User, Alarm, Notification, Video, Complex, Rate


async def create_complexes(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                "description": "Описание комплекса 1",
                "name": "комплекс 1",
                "number": 1,
                "duration": 0
            },
            {
                "description": "Описание комплекса 2",
                "name": "комплекс 2",
                "number": 2,
                "duration": 0
            },
            {
                "description": "Описание комплекса 3",
                "name": "комплекс 3",
                "number": 3,
                "duration": 0
            },
            {
                "description": "Описание комплекса 4",
                "name": "комплекс 4",
                "number": 4,
                "duration": 0
            }
        ]

    for compl in data:
        await Complex.add_new(session=session, **compl)


async def create_videos(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                "complex_id": 1,
                'file_name': 'test.mp4',
                'description': f'описание видео {i}',
                'name': f'Видео № {i}',
                'duration': i * 100 + 10 * i,
                'number': i

            }
            for i in range(1, 6)
        ]
        data2 = [
            {
                "complex_id": 2,
                'file_name': 'test.mp4',
                'description': f'описание 2 видео {i}',
                'name': f'Видео 2 № {i}',
                'duration': i * 100 + 20 * i,
                'number': i
            }
            for i in range(1, 6)
        ]
        data.extend(data2)

    for video in data:
        await Video.add_new(session=session, **video)


async def create_users(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                'username': "asd",
                'last_name': "asdl",
                'third_name': "asdt",
                'phone': "1234567890",
                'gender': 1,
                'password': "asd",
                'email': "asd@asd.ru",
                'current_complex': 1,
                'rate_id': 1,
                'is_admin': True,
                'is_active': False,
                'is_verified': True
            },
            {
                'username': "test2",
                'last_name': "test2last",
                'phone': "1234567892",
                'gender': 0,
                'password': "test2pass",
                'email': 'test2@email.com',
                'current_complex': 1,
                'rate_id': 1,
                'is_admin': False,
                'is_active': True

            },
            {
                'username': "test3",
                'phone': "1234567893",
                'password': "test3pass",
                'gender': 0,
                'email': 'test3@email.com',
                'current_complex': 1,
                'rate_id': 2,
                'is_admin': False,
                'is_active': False
            },
        ]
    for user in data:
        expired_at = datetime.utcnow() + timedelta(days=30)
        user['password'] = await User.get_hashed_password(user['password'])
        user = User(**user, expired_at=expired_at)
        session.add(user)
    await session.commit()


async def create_alarms(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                'alarm_time': '10:00',
                'text': 'alarm1',
                'user_id': 1
            },
            {
                'alarm_time': '11:00',
                'text': 'alarm2',
                'user_id': 1
            },
            {
                'alarm_time': '13:00',
                'text': 'alarm3',
                'user_id': 2
            },
        ]
    for alarm in data:
        session.add(Alarm(**alarm))
    await session.commit()


async def create_notifications(session: AsyncSession, data: list[dict] = None):
    today = datetime.today()

    if not data:
        data = [
            {
                'created_at': today,
                'text': 'notification1',
                'user_id': 1
            },
            {
                'created_at': today,
                'text': 'notification2',
                'user_id': 1
            },
            {
                'created_at': today,
                'text': 'notification3',
                'user_id': 2
            },
        ]
    for notification in data:
        session.add(Notification(**notification))
    await session.commit()


async def create_rates(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                'name': 'Бесплатный',
                'price': 0,
                'duration': 30
            },
            {
                'name': '30 дней',
                'price': 100,
                'duration': 30
            },
            {
                'name': '6 месяцев',
                'price': 500,
                'duration': 30 * 6
            }
        ]
    for elem in data:
        session.add(Rate(**elem))
    await session.commit()


async def create_fake_data(flag: bool = False):
    """Create fake data in database"""
    if settings.CREATE_FAKE_DATA or flag:
        async for session in get_db_session():
            logger.debug("Create fake data to DB")
            if await session.get(User, 1):
                return
            await create_rates(session)
            await create_complexes(session)
            await create_videos(session)
            await create_users(session)
            await create_alarms(session)
            await create_notifications(session)
            await create_default_admin()
            logger.debug("Create fake data to DB: OK")


async def recreate_db(drop=False) -> None:
    """Drop and create tables in database"""

    if drop or settings.RECREATE_DB:
        await drop_db()
        await create_db()


if __name__ == '__main__':
    async def make(flag, drop):
        await recreate_db(drop)
        await create_fake_data(flag)


    flag = True
    drop = True
    asyncio.run(make(flag, drop))
