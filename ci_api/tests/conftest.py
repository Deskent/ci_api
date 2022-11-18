from datetime import datetime, timedelta
from pathlib import Path

import pytest
import requests

from pydantic import EmailStr, BaseSettings
from pydantic.dataclasses import dataclass

from services.auth import AuthHandler
from main import app
from fastapi.testclient import TestClient


class Config(BaseSettings):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000


BASE_DIR = Path(__file__).parent.parent
env_file = BASE_DIR / '.env'
test_config = Config(_env_file=env_file, _env_file_encoding='utf-8')


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


@pytest.fixture
def test_app():
    with requests.Session() as session:
        yield session
    # with TestClient(app) as session:
    #     yield session


@pytest.fixture
def base_url():
    return f"http://{test_config.SERVER_HOST}:{test_config.SERVER_PORT}/api/v1"


@pytest.fixture
def user_payload():
    user = TestUser()
    return {"email": user.email, "password": user.password}


@pytest.fixture
def user_create():
    return CreateUser().as_dict()


@pytest.fixture
def get_bearer(user_payload, base_url):
    url = base_url + "/auth/login"
    response = requests.post(url, json=user_payload)
    token = response.json().get('token')

    return {'Authorization': f"Bearer {token}"}


@pytest.fixture
def token(base_url, get_bearer):
    response = requests.get(base_url + "/users/me", headers=get_bearer)
    user = TestUser(**response.json())
    return AuthHandler().get_email_token(user)


@pytest.fixture
def new_alarm():
    return {
        "alarm_time": "10:10",
        "weekdays": ["monday", "friday"],
        "sound_name": "some name",
        "volume": 20,
        "vibration": False,
        "text": "test"
    }
