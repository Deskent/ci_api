from datetime import datetime, timedelta

import pytest
import requests
from pydantic import EmailStr
from pydantic.dataclasses import dataclass

from services.auth import AuthHandler


@dataclass
class CreateUser:
    username: str = "test"
    email: EmailStr = "test@test.ru"
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
def base_url():
    return "http://127.0.0.1:8000/api/v1"


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
