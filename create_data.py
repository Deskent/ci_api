from datetime import datetime, timedelta

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from database.db import engine, drop_db, create_db, db

from models.models import *


async def recreate() -> None:
    if not db.RECREATE_DB:
        return

    await drop_db()
    await create_db()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    videos_data = [
        {
            'path': 'media/hello.mp4',
            'description': 'some video',
            'name': 'v1',
            'previous_id': None,
            'next_id': 2
        },
        {
            'path': 'media/hello.mp4',
            'name': 'v2',
            'description': 'some video',
            'previous_id': 1,
            'next_id': 3
        },
        {
            'path': 'media/hello.mp4',
            'name': 'v3',
            'description': 'some video',
            'previous_id': 2,
            'next_id': 4
        },
    ]
    alarm_data = [
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
    notifications_data = [
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
    user_data = [
        {
            'username': "test1",
            'password': "test1pass",
            'email': 'test1@email.com',
            'current_video': 1,
            'is_admin': True,
            'is_active': True
        },
        {
            'username': "test2",
            'password': "test2pass",
            'email': 'test2@email.com',
            'current_video': 1,
            'is_admin': False,
            'is_active': True

        },
        {
            'username': "test3",
            'password': "test3pass",
            'email': 'test3@email.com',
            'current_video': 1,
            'is_admin': False,
            'is_active': False
        },
    ]

    async with async_session() as session:

        for video in videos_data:
            elem = Video(**video)
            session.add(elem)

        await session.commit()

        for user in user_data:
            expired_at = datetime.utcnow() + timedelta(days=30)
            user = User(**user, expired_at=expired_at)
            session.add(user)

        await session.commit()

        for alarm in alarm_data:
            alarm_instance = Alarm(**alarm)
            session.add(alarm_instance)

        await session.commit()

        for notification in notifications_data:
            elem = Notification(**notification)
            session.add(elem)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(recreate())
