from datetime import datetime, timedelta

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import logger
from database.db import engine, drop_db, create_db, db, get_session
from services.auth import auth_handler
from models.models import User, Alarm, Notification, Video, Complex


async def create_complexes(data: list[dict] = None):
    if not data:
        data = [
            {
                "description": "complex1"
            },
            {
                "description": "complex2"
            }
        ]

    for compl in data:
        await Complex(**compl).save()


async def create_videos(data: list[dict] = None):
    if not data:
        data = [
            {
                "complex_id": 1,
                'file_name': 'hello.mp4',
                'description': 'some video',
                'name': 'v1',
            },
            {
                "complex_id": 1,
                'file_name': 'hello.mp4',
                'name': 'v2',
                'description': 'some video',
            },
            {
                "complex_id": 1,
                'file_name': 'hello.mp4',
                'name': 'v3',
                'description': 'some video',
            },
        ]

    for video in data:
        await Video(**video).save()


async def create_users(data: list[dict] = None):
    if not data:
        data = [
            {
                'username': "admin",
                'phone': "7777777777",
                'gender': 1,
                'password': "admin",
                'email': "admin@bk.ru",
                'current_complex': 1,
                'is_admin': True,
                'is_active': True
            },
            {
                'username': "test1",
                'phone': "1234567890",
                'gender': 1,
                'password': "string",
                'email': "test1@example.com",
                'current_complex': 1,
                'is_admin': True,
                'is_active': False
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
    for user in data:
        expired_at = datetime.utcnow() + timedelta(days=30)
        user['password'] = auth_handler.get_password_hash(user['password'])
        user = User(**user, expired_at=expired_at)
        await user.save()


async def create_alarms(data: list[dict] = None):
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
        await Alarm(**alarm).save()


async def create_notifications(data: list[dict] = None):
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
        await Notification(**notification).save()


async def create_test():
    userdata = {
                'notification_time': '18:00',
                'text': 'notification8',
                'user_id': 1
            }
    notif = Notification(**userdata)
    await notif.save()


async def create_fake_data():
    logger.debug("Create fake data to DB")
    await create_complexes()
    await create_videos()
    await create_users()
    await create_alarms()
    await create_notifications()
    await create_test()


async def recreate(flag: bool = False) -> None:
    if db.RECREATE_DB or flag:
        await drop_db()
        await create_db()
        await create_fake_data()


if __name__ == '__main__':
    flag = True
    asyncio.run(recreate(flag))
