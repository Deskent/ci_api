import asyncio
from datetime import datetime, timedelta

from admin.utils import create_default_admin
from config import logger, settings
from database.db import drop_db, create_db
from database.models import Complex, Rate, Video
from crud_class.crud import CRUD


async def create_complexes(data: list[dict] = None):
    logger.debug(f"Create data")

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
        await CRUD.complex.create(compl)


async def create_videos(data: list[dict] = None):
    logger.debug(f"Create data")
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
        await CRUD.video.create(video)


async def create_users(data: list[dict] = None):
    logger.debug(f"Create data")

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
                'expired_at': datetime.now() + timedelta(days=30),
            },
            {
                'username': "ppp",
                'last_name': "ppp",
                'third_name': "ppp",
                'phone': "1111111111",
                'gender': 1,
                'password': "ppp",
                'email': "ppp@ppp.ru",
                'is_active': True,
                'is_verified': True,
                'rate_id': 2,
                'expired_at': datetime.now() + timedelta(days=1),
                'last_entry': datetime.now() + timedelta(days=-1),
                'level': 7
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
        first_complex: Complex = await CRUD.complex.get_first()
        user_data['current_complex'] = first_complex.id
        if not user_data.get('rate_id'):
            free_rate: Rate = await CRUD.rate.get_free()
            if free_rate:
                user_data['rate_id'] = free_rate.id
        user_data['avatar'] = await CRUD.avatar.get_first_id()
        await CRUD.user.create(user_data)


async def create_alarms(data: list[dict] = None):
    logger.debug(f"Create data")

    if not data:
        data = [
            {
                'alarm_time': '10:00',
                'text': 'alarm1',
                'user_id': 1,
                'weekdays': ['all']
            },
            {
                'alarm_time': '11:00',
                'text': 'alarm2',
                'user_id': 1,
                'weekdays': ['all']
            },
            {
                'alarm_time': '13:00',
                'text': 'alarm3',
                'user_id': 2,
                'weekdays': ['all']
            },
        ]
    for alarm in data:
        await CRUD.alarm.create(alarm)


async def create_notifications(data: list[dict] = None):
    logger.debug(f"Create data")

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
        await CRUD.notification.create(notification)


async def create_rates(data: list[dict] = None):
    logger.debug(f"Create data")

    if not data:
        data = [
            {
                'name': 'Free',
                'price': 0,
                'duration': 30
            },
            {
                'name': 'Солнце',
                'price': 199,
                'duration': 30
            },
        ]
    for elem in data:
        await CRUD.rate.create(elem)


async def create_moods(data: list[dict] = None):
    if not data:
        data = [
            {
                'name': 'Все бесят',
                'code': 'U+1F621'
            },
            {
                'name': 'Печалька-тоска',
                'code': 'U+1F61E'
            },
            {
                'name': 'Нервно-тревожно',
                'code': 'U+1F910'
            },
            {
                'name': 'Бодрячок',
                'code': 'U+1F601'
            },
            {
                'name': 'Всех люблю',
                'code': 'U+1F970'
            },
        ]
    for elem in data:
        await CRUD.mood.create(elem)
    logger.debug(f"Create data")


async def create_avatars(data: list[dict] = None):
    if not data:
        data = [
            {
                'file_name': 'avatar.svg',
            },
        ]
    for elem in data:
        path = settings.MEDIA_DIR / 'avatars' / elem['file_name']
        if not path.exists():
            raise ValueError(f"Avatar default file not found: {path}")
        await CRUD.avatar.create(elem)
    logger.debug(f"Create data")


async def create_fake_data(flag: bool = False):
    """Create fake data in database"""

    if settings.CREATE_FAKE_DATA or flag:
        logger.debug("Create fake data to DB")
        if await CRUD.user.get_by_id(1, use_cache=False):
            return
        await create_rates()
        await create_moods()
        await create_avatars()
        await create_complexes()
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


async def create_default_data():
    complex_data = [
        {
            "description": "Описание комплекса 1",
            "name": "комплекс 1",
            "number": 1,
            "duration": 0
        },
    ]

    videos_data = [
        {
            "complex_id": 1,
            'file_name': 'e1c1.mp4',
            'description': f'описание видео {1}',
            'name': f'Видео № {1}',
            'duration': 75,
            'number': 1
        },
        {
            "complex_id": 1,
            'file_name': 'e2c1.mp4',
            'description': f'описание видео {2}',
            'name': f'Видео № {2}',
            'duration': 66,
            'number': 2
        },
        {
            "complex_id": 1,
            'file_name': 'e3c1.mp4',
            'description': f'описание видео {3}',
            'name': f'Видео № {3}',
            'duration': 90,
            'number': 3
        },
        {
            "complex_id": 1,
            'file_name': 'e4c1.mp4',
            'description': f'описание видео {4}',
            'name': f'Видео № {4}',
            'duration': 75,
            'number': 4
        },
        {
            "complex_id": 1,
            'file_name': 'e5c1.mp4',
            'description': f'описание видео {5}',
            'name': f'Видео № {5}',
            'duration': 66,
            'number': 5
        },
    ]

    hello_video = [
        {
            'file_name': 'hello.mp4',
            'description': f'Приветственное видео',
            'name': f'Приветственное видео',
            'duration': 30,
            'number': 1
        }
    ]
    videos: list[Video] = await CRUD.video.get_all(False)
    if not videos:
        if not await CRUD.complex.get_all(False):
            await create_complexes(complex_data)
        await create_videos(videos_data)
    if not await CRUD.video.get_hello_video():
        await create_videos(hello_video)
    if not await CRUD.rate.get_all(False):
        await create_rates()
    if not await CRUD.avatar.get_all(False):
        await create_avatars()
    if not await CRUD.mood.get_all(False):
        await create_moods()


if __name__ == '__main__':
    async def make(flag, drop):
        await recreate_db(drop)
        await create_fake_data(flag)
        await create_default_data()


    flag = True
    drop = True
    asyncio.run(make(flag, drop))
