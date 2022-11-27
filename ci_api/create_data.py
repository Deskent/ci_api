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
                "description": "complex1",
                "name": "комплекс 1",
                "next_complex_id": 2,
                "duration": 10
            },
            {
                "description": "complex2",
                "name": "комплекс 2",
                "next_complex_id": 3,
                "duration": 20
            }
        ]

    for compl in data:
        session.add(Complex(**compl))
    await session.commit()


async def create_videos(session: AsyncSession, data: list[dict] = None):
    if not data:
        data = [
            {
                "complex_id": 1,
                'file_name': 'test.mp4',
                'description': 'some video',
                'name': 'v1',
            },
            {
                "complex_id": 1,
                'file_name': 'test.mp4',
                'name': 'v2',
                'description': 'some video2',
            },
            {
                "complex_id": 1,
                'file_name': 'test.mp4',
                'name': 'v3',
                'description': 'some video3',
            },
        ]

    for video in data:
        session.add(Video(**video))
    await session.commit()


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
                'is_active': False
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
    if not data:
        data = [
            {
                'notification_time': '10:00',
                'text': 'notification1',
                'user_id': 1
            },
            {
                'notification_time': '11:00',
                'text': 'notification2',
                'user_id': 1
            },
            {
                'notification_time': '12:00',
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
                'name': '1 month rate',
                'price': 100,
                'duration': 30
            },
            {
                'name': '6 month rate',
                'price': 500,
                'duration': 30 * 6
            }
        ]
    for elem in data:
        session.add(Rate(**elem))
    await session.commit()


async def create_fake_data(flag: bool = False):
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


async def recreate_db(drop = False):
    if drop:
        await drop_db()
        await create_db()


async def make(flag, drop):
    await recreate_db(drop)
    await create_fake_data(flag)


if __name__ == '__main__':
    flag = True
    drop = False
    asyncio.run(make(flag, drop))
