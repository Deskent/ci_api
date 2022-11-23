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
        self.notification_id = setup_class.notification_id
        yield

    def test_get_me(self):
        response = self.session.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get("id") is not None

    def test_verify_email(self):
        url = self.base_url + "/auth/verify_email" + f"?token={self.email_token}"
        response = self.session.get(url)
        assert response.status_code == 202

    def test_login_endpoint(self):
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    def test_get_user_alarms(self):
        response = self.session.get(self.base_url + "/users/alarms", headers=self.headers)
        assert response.status_code == 200

    def test_get_user_notifications(self):
        response = self.session.get(self.base_url + "/users/notifications", headers=self.headers)
        assert response.status_code == 200

    def test_change_password(self):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = self.session.put(
            self.base_url + "/auth/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202

    def test_get_video_by_id(self):
        response = self.session.get(self.base_url + "/videos/1", headers=self.headers)
        assert response.status_code == 200

    def test_get_notification_by_id(self):
        response = self.session.get(
            self.base_url + f"/notifications/{self.notification_id}", headers=self.headers)
        assert response.status_code == 200

    def test_get_alarm(self):
        response = self.session.get(self.base_url + f"/alarms/{self.alarm_id}", headers=self.headers)
        assert response.status_code == 200

    def test_get_rates(self):
        response = self.session.get(self.base_url + "/users/rates")
        assert response.status_code == 200
