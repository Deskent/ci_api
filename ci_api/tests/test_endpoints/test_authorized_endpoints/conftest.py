from datetime import datetime, timedelta

import pytest
from pydantic import EmailStr
from pydantic.dataclasses import dataclass

from services.utils import get_current_datetime


@dataclass
class CreateUser:
    username: str = "test"
    last_name: str = "testov"
    third_name: str = "testovich"
    email: EmailStr = "test@mail.ru"
    phone: str = "9998887711"
    password: str = "testpassword"
    password2: str = "testpassword"
    gender: bool = True
    test: bool = True
    is_active: bool = True

    def as_dict(self):
        return self.__dict__

    def headers(self):
        return {"phone": self.phone, "password": self.password}


@dataclass
class TestUser(CreateUser):
    id: int = None
    level: int = 1
    progress: int = 0
    created_at: datetime = get_current_datetime()
    expired_at: datetime = get_current_datetime() + timedelta(days=30)
    is_verified: bool = False
    is_admin: bool = False
    is_active: bool = True
    current_complex: int = 1


@pytest.fixture(scope='session')
def test_user():
    return TestUser


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


class CreateEndpointUserData:
    def __init__(
            self: 'CreateEndpointUserData',
            session,
            base_url: str,
            new_alarm: dict,
    ):
        self.session = session
        self.base_url: str = base_url
        self.new_alarm: dict = new_alarm

        self.user_create = CreateUser()
        self.test_user: TestUser | None = None
        self.user_payload: dict = self.user_create.headers()
        self.headers = {}
        self.email_token: str = ''
        self.token: str = ''
        self.alarm_id: int = 0
        self.push_token: str = 'test_push_token'

    def create_user(self) -> dict:
        response = self.session.post(
            self.base_url + "/auth/register",
            json=self.user_create.as_dict())
        assert response.status_code == 200
        data = response.json()
        self.test_user = TestUser(id=data['id'])

        return data

    def login_user(self) -> dict:
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get('token')

        self.headers = {'Authorization': f"Bearer {token}"}

        return self.headers

    def create_alarm(self) -> int:
        response = self.session.post(
            self.base_url + "/alarms", headers=self.headers, json=self.new_alarm,
            allow_redirects=True
        )
        assert response.status_code == 200
        alarm_id = response.json().get("id")
        assert alarm_id
        self.alarm_id = alarm_id

        return alarm_id

    def create_push_token(self) -> None:
        response = self.session.put(
            self.base_url + "/users/set_push_token", headers=self.headers, json=self.push_token
        )
        assert response.status_code == 202

    def delete_user(self) -> None:
        response = self.session.delete(
            self.base_url + "/users",
            headers=self.headers, allow_redirects=True)
        assert response.status_code == 204

    def create(self) -> None:
        self.create_user()
        self.login_user()
        self.create_push_token()
        self.create_alarm()


@pytest.fixture(scope='class')
def setup_class(
        get_test_client_app, base_url, user_create, new_alarm,
        test_user
) -> CreateEndpointUserData:
    test_data = CreateEndpointUserData(
        session=get_test_client_app, base_url=base_url, new_alarm=new_alarm
    )
    try:
        test_data.create()
        yield test_data
    finally:
        test_data.delete_user()
