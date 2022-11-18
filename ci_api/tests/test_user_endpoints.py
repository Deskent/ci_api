import pytest
import requests


class TestUsers:

    def create_user(self):
        response = requests.post(self.base_url + "/auth/register", json=self.user_create)
        assert response.status_code == 200
        response = requests.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get('token')

        return {'Authorization': f"Bearer {token}"}

    def delete_user(self):
        response = requests.delete(self.base_url + "/users", headers=self.headers)
        assert response.status_code == 204

    @pytest.fixture()
    def setUp(self, base_url, user_create, user_payload):
        self.base_url = base_url
        self.user_create = user_create
        self.user_payload = user_payload
        self.headers = self.create_user()
        yield self.headers
        self.delete_user()

    def test_get_me(self, setUp):
        response = requests.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get("id") is not None

    def test_verify_email(self, setUp, token):
        url = self.base_url + "/auth/verify_email" + f"?token={token}"
        response = requests.get(url)
        assert response.status_code == 202

    def test_login_endpoint(self, setUp):
        response = requests.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    def test_get_user_alarms(self, setUp):
        response = requests.get(self.base_url + "/users/alarms", headers=self.headers)
        assert response.status_code == 200

    def test_get_user_notifications(self, setUp):
        response = requests.get(self.base_url + "/users/notifications", headers=self.headers)
        assert response.status_code == 200

    def test_change_password(self, setUp):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = requests.put(self.base_url + "/auth/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202
