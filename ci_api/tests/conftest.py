from datetime import datetime, timedelta

import fastapi.testclient
import pytest

from pydantic import EmailStr
from pydantic.dataclasses import dataclass

from services.auth import AuthHandler
from main import app


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
def get_app():
    return app


@pytest.fixture(scope='session')
def get_test_app(get_app):
    client = fastapi.testclient.TestClient(app=get_app)
    with client as session:
        yield session


@pytest.fixture
def base_url():
    return "/api/v1"


@pytest.fixture
def user_payload():
    user = TestUser()
    return {"email": user.email, "password": user.password}


@pytest.fixture
def user_create():
    return CreateUser().as_dict()


@pytest.fixture
def get_bearer(get_test_app, base_url, user_payload):
    url = base_url + "/auth/login"
    response = get_test_app.post(url, json=user_payload)
    token = response.json().get('token')

    return {'Authorization': f"Bearer {token}"}


@pytest.fixture
def token(get_test_app, base_url, get_bearer):
    response = get_test_app.get(base_url + "/users/me", headers=get_bearer)
    user = TestUser(**response.json())
    return AuthHandler().get_email_token(user)


@pytest.fixture
def new_alarm():
    return {
        "alarm_time": "10:10",
        "weekdays": ["monday", "friday"],
        "sound_name": "test name",
        "volume": 20,
        "vibration": False,
        "text": "test text"
    }


@pytest.fixture
def new_notification():
    return {
        "notification_time": "11:10",
        "text": "test notification text"
    }
