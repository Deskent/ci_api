import datetime

import pytest


class TestUsers:

    @pytest.fixture(autouse=True)
    def setUp(self, setup_class):
        self.session = setup_class.session
        self.test_user = setup_class.test_user
        self.base_url = setup_class.base_url
        self.user_create = setup_class.user_create
        self.user_payload = setup_class.user_payload
        self.headers = setup_class.headers
        self.email_token = setup_class.email_token
        self.alarm_id = setup_class.alarm_id
        self.user_id = None
        yield

    @pytest.mark.server
    def test_get_me(self):
        response = self.session.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        user_id = data.get("email")
        assert user_id is not None
        assert data.get('max_level') is not None
        self.user_id = user_id

    @pytest.mark.server
    def test_login_endpoint(self):
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    @pytest.mark.server
    def test_change_password(self):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = self.session.put(
            self.base_url + "/auth/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202

    @pytest.mark.skip('Need activate user')
    def test_get_video_by_id(self, event_loop):
        response = self.session.get(self.base_url + f"/complex/1/", headers=self.headers)
        assert response.status_code == 200
        complexes: dict = response.json()
        video_id: int = complexes['videos'][0].get('id')
        response = self.session.get(self.base_url + f"/videos/{video_id}/", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        assert data is not None
        assert data.get('id') is not None

    @pytest.mark.server
    def test_create_notification(self):
        payload = {
            "created_at": f"{datetime.datetime.now()}",
            "text": "Test notif"
        }
        response = self.session.post(
            self.base_url + f"/notifications/", headers=self.headers, json=payload)
        assert response.status_code == 200
        data: dict = response.json()
        assert data is not None
        assert data.get('id') is not None

    @pytest.mark.server
    def test_get_notifications(self):
        response = self.session.get(
            self.base_url + f"/users/notifications/", headers=self.headers)
        assert response.status_code == 200
        notifications: list[dict] = response.json()
        notification_id = notifications[0].get("id")
        assert notification_id is not None

        response = self.session.get(
            self.base_url + f"/notifications/{notification_id}/", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.server
    def test_get_alarm(self):
        response = self.session.get(self.base_url + f"/alarms/{self.alarm_id}", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.server
    def test_get_rates(self):
        response = self.session.get(self.base_url + "/users/rates")
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.server
    def test_all_for_complex_id(self):
        response = self.session.get(self.base_url + "/videos/all_for/1", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.server
    def test_get_alarms_list(self):
        response = self.session.get(self.base_url + "/users/alarms/list", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.server
    def test_get_complexes_list(self):
        response = self.session.get(self.base_url + "/complex/list", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        assert data.get('user') is not None
        assert data.get('complexes') is not None


    @pytest.mark.server
    def test_get_viewed_complexes_list(self):
        response = self.session.get(self.base_url + "/complex/viewed/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get('viewed') is not None
        assert data.get('user') is not None
        assert data.get('complexes') is not None

    @pytest.mark.server
    def test_set_viewed_complex(self):
        response = self.session.get(self.base_url + "/complex/complex_viewed/1", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get('level_up') is not None

    # TODO исправить
    @pytest.mark.skip("Not delete relations viewed video")
    def test_viewed_video_endpoint(self):
        data = {
            "user_tel": self.test_user.phone,
            "video_id": 1
        }
        response = self.session.post(self.base_url + "/videos/viewed", json=data)
        assert response.status_code == 200
        data: dict = response.json()
        assert data['user'] is not None

    @pytest.mark.skip("Need to know verify code from database")
    def test_verify_email(self):
        url = self.base_url + "/auth/verify_email" + f"?token={self.email_token}"
        response = self.session.get(url)
        assert response.status_code == 202
