import pytest

from crud_class.crud import CRUD
from database.models import Video, Complex, User, Alarm


@pytest.fixture
async def get_complex():
    data = {
        "description": "Описание комплекса 99",
        "name": "комплекс 99",
        "number": 99,
        "duration": 99
    }
    complex: Complex = await CRUD.complex.create(data)
    yield complex
    await CRUD.complex.delete(complex)


@pytest.fixture
async def get_video(get_complex):
    data = {
        "description": "Описание video 99",
        "name": "video 99",
        "number": 99,
        "duration": 99,
        "complex_id": get_complex.id,
        "file_name": "text_name.mp4"
    }
    video: Video = await CRUD.video.create(data)
    yield video
    await CRUD.video.delete_by_id(video.id)


@pytest.fixture
def user_data():
    return {
        'username': "asddd",
        'last_name': "asdldd",
        'third_name': "asdtdd",
        'phone': "0234567890",
        'gender': 1,
        'password': "asd",
        'email': "asddd@asddd.ru",
        'rate_id': 1
    }


@pytest.fixture
async def get_user(user_data):
    user: User = await CRUD.user.get_by_email(user_data['email'])
    if user:
        await CRUD.user.delete(user)
    user: User = await CRUD.user.create(user_data)
    yield user
    await CRUD.user.delete(user)


@pytest.fixture
async def get_user_alarm(get_user):
    data = {
        'alarm_time': '10:00',
        'text': 'test_alarm1',
        'user_id': get_user.id,
    }
    alarm: Alarm = await CRUD.alarm.create(data)
    yield alarm
    await CRUD.alarm.delete(alarm)
