import asyncio
from datetime import datetime, timedelta


from admin.utils import create_default_admin
from config import logger, settings
from database.db import drop_db, create_db
from models.models import User, Alarm, Notification, Video, Complex, Rate


async def create_complexes(data: list[dict] = None):
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
        await Complex.add_new(**compl)


async def create_videos(data: list[dict] = None):
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
        await Video.add_new(**video)


async def create_users(data: list[dict] = None):
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
                'is_active': True,
                'is_verified': True,
                'rate_id': 2,
                'expired_at': datetime.now() + timedelta(days=30)
            },
            {
                'username': "test2",
                'last_name': "test2last",
                'phone': "1234567892",
                'gender': 0,
                'password': "asd",
                'email': 'test2@email.com',
                'is_active': True

            },
            {
                'username': "test3",
                'phone': "1234567893",
                'password': "asd",
                'gender': 0,
                'email': 'test3@email.com',
                'is_active': False
            },
        ]
    for user_data in data:
        first_complex: Complex = await Complex.get_first()
        user_data['current_complex'] = first_complex.id
        if not user_data.get('rate_id'):
            free_rate: Rate = await Rate.get_free()
            if free_rate:
                user_data['rate_id'] = free_rate.id
        await User.create(user_data)


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
        alarm = Alarm(**alarm)
        await alarm.save()


async def create_notifications(data: list[dict] = None):
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
                'user_id': 2
            },
            {
                'created_at': today,
                'text': 'notification3',
                'user_id': 3
            },
        ]
    for notification in data:
        elem = Notification(**notification)
        await elem.save()


async def create_rates(data: list[dict] = None):
    if not data:
        data = [
            {
                'name': 'Free',
                'price': 0,
                'duration': 30
            },
            {
                'name': 'Солнце',
                'price': 999,
                'duration': 30
            },
            {
                'name': 'Инь-ян',
                'price': 1990,
                'duration': 30
            },
            {
                'name': 'Энергия жизни',
                'price': 2900,
                'duration': 30 * 6
            }
        ]
    for elem in data:
        elem = Rate(**elem)
        await elem.save()


async def create_fake_data(flag: bool = False):
    """Create fake data in database"""

    if settings.CREATE_FAKE_DATA or flag:
        logger.debug("Create fake data to DB")
        if await User.get_by_id(1):
            return
        await create_rates()
        await create_complexes()
        await create_videos()
        await create_users()
        await create_alarms()
        await create_notifications()
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
