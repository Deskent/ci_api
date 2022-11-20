from datetime import datetime, timedelta

import pytest

from pydantic import EmailStr
from pydantic.dataclasses import dataclass


@dataclass
class CreateUser:
    username: str = "test"
    email: EmailStr = "test@mail.ru"
    phone: str = "9998887711"
    password: str = "testpassword"
    password2: str = "testpassword"
    gender: bool = True

    def as_dict(self):
        return self.__dict__


@dataclass
class TestUser(CreateUser):
    id: int = None
    level: int = 1
    progress: int = 0
    created_at: datetime = datetime.now(tz=None)
    expired_at: datetime = datetime.now(tz=None) + timedelta(days=30)
    is_verified: bool = False
    is_admin: bool = False
    is_active: bool = False
    current_complex: int = 1


@pytest.fixture(scope='session')
def test_user():
    return TestUser


@pytest.fixture(scope='session')
def user_payload(test_user):
    user = test_user()
    return {"email": user.email, "password": user.password}


@pytest.fixture(scope='session')
def user_create():
    return CreateUser().as_dict()


@pytest.fixture(scope='session')
def new_alarm():
    return {
        "alarm_time": "10:10",
        "weekdays": ["monday", "friday"],
        "sound_name": "test name",
        "volume": 20,
        "vibration": False,
        "text": "test text"
    }


@pytest.fixture(scope='session')
def new_notification():
    return {
        "notification_time": "11:10",
        "text": "test notification text"
    }
