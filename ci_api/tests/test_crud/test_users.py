import pytest

from models.models import User, Rate, Complex, Alarm
from services.models_cache.crud import CRUD


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


async def test_crud_get_user_by_id():
    user: User = await CRUD.user.get_by_id(1)
    assert user.id == 1
    user: User = await CRUD.user.get_by_id(2)
    assert user.id == 2


async def test_crud_get_all_users():
    users: list[User] = await CRUD.user.get_all()
    assert users[0].email is not None


async def test_crud_get_all_rates():
    data: list[Rate] = await CRUD.rate.get_all()
    assert data[0].name == 'Free'


async def test_crud_get_all_complexes():
    data: list[Complex] = await CRUD.complex.get_all()
    assert data[0].duration is not None


async def test_crud_create_user(user_data):
    user: User = await CRUD.user.get_by_email(user_data['email'])
    if user:
        await CRUD.user.delete(user)
    user: User = await CRUD.user.create(user_data)
    assert user.username == user_data['username']


async def test_crud_get_user_by_phone(user_data):
    user: User = await CRUD.user.get_by_phone(user_data['phone'])
    assert user.phone == user_data['phone']


async def test_crud_activate_user(user_data):
    user: User = await CRUD.user.get_by_phone(user_data['phone'])
    user: User = await CRUD.user.activate(user)
    assert user.is_active == True
    user: User = await CRUD.user.deactivate(id_=user.id)
    assert user.is_active == False


async def test_crud_get_alarm_by_id():
    user: User = await CRUD.user.get_by_id(1)
    alarm: Alarm = await CRUD.user.get_alarm_by_id(user, 1)
    assert alarm.id == 1


async def test_crud_delete_user(user_data):
    user: User = await CRUD.user.get_by_email(user_data['email'])
    if user:
        await CRUD.user.delete(user)
