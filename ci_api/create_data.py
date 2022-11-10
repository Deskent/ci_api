from datetime import datetime, timedelta

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.db import engine, drop_db, create_db, db
from services.auth import AuthHandler
from models.models import User, Alarm, Notification, Video, Complex


auth_handler = AuthHandler()


async def create_complexes(data: list[dict] = None):
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
    if not data:
        data = [
            {
                "description": "complex1"
            },
            {
                "description": "complex2",
            },
        ]
    async with async_session() as session:

        for compl in data:
            elem = Complex(**compl)
            session.add(elem)

        await session.commit()


async def create_videos(data: list[dict] = None):
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
    if not data:
        data = [
            {
                "complex_id": 1,
                'path': 'media/hello.mp4',
                'description': 'some video',
                'name': 'v1',
            },
            {
                "complex_id": 1,
                'path': 'media/hello.mp4',
                'name': 'v2',
                'description': 'some video',
            },
            {
                "complex_id": 1,
                'path': 'media/hello.mp4',
                'name': 'v3',
                'description': 'some video',
            },
        ]

    async with async_session() as session:

        for video in data:
            elem = Video(**video)
            session.add(elem)

        await session.commit()


async def create_users(data: list[dict] = None):
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
    if not data:
        data = [
            {
                'username': "test1",
                'phone': "1234567890",
                'gender': 1,
                'password': "string",
                'email': "user@example.com",
                'current_complex': 1,
                'is_admin': True,
                'is_active': True
            },
            {
                'username': "test2",
                'phone': "1234567892",
                'gender': 1,
                'password': "test2pass",
                'email': 'test2@email.com',
                'current_complex': 1,
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
                'is_admin': False,
                'is_active': False
            },
        ]
    async with async_session() as session:

        for user in data:
            expired_at = datetime.utcnow() + timedelta(days=30)
            user['password'] = auth_handler.get_password_hash(user['password'])
            user = User(**user, expired_at=expired_at)
            session.add(user)

        await session.commit()


async def create_alarms(data: list[dict] = None):
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
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
    async with async_session() as session:

        for alarm in data:
            alarm_instance = Alarm(**alarm)
            session.add(alarm_instance)

        await session.commit()


async def create_notifications(data: list[dict] = None):
    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
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
    async with async_session() as session:
        for notification in data:
            elem = Notification(**notification)
            session.add(elem)

        await session.commit()


async def create_fake_data():
    await create_complexes()
    await create_videos()
    await create_users()
    await create_alarms()
    await create_notifications()


async def recreate(flag: bool = False) -> None:
    if not db.RECREATE_DB and not flag:
        return

    await drop_db()
    await create_db()
    await create_fake_data()


if __name__ == '__main__':
    flag = True
    asyncio.run(recreate(flag))
