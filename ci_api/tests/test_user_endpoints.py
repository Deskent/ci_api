import pytest


class TestUsers:

    def create_user(self):
        response = self.session.post(self.base_url + "/auth/register", json=self.user_create)
        assert response.status_code == 200
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get('token')

        return {'Authorization': f"Bearer {token}"}

    def delete_user(self):
        response = self.session.delete(self.base_url + "/users", headers=self.headers)
        assert response.status_code == 204

    @pytest.fixture
    def setUp(self, test_app, base_url, user_create, user_payload):
        self.session = test_app
        self.base_url = base_url
        self.user_create = user_create
        self.user_payload = user_payload
        self.headers = self.create_user()
        yield self.headers
        self.delete_user()

    def test_get_me(self, setUp):
        response = self.session.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get("id") is not None

    def test_verify_email(self, setUp, token):
        url = self.base_url + "/auth/verify_email" + f"?token={token}"
        response = self.session.get(url)
        assert response.status_code == 202

    def test_login_endpoint(self, setUp):
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    def test_get_user_alarms(self, setUp):
        response = self.session.get(self.base_url + "/users/alarms", headers=self.headers)
        assert response.status_code == 200

    def test_get_user_notifications(self, setUp):
        response = self.session.get(self.base_url + "/users/notifications", headers=self.headers)
        assert response.status_code == 200

    def test_change_password(self, setUp):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = self.session.put(self.base_url + "/auth/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202

    def test_get_video_by_id(self, setUp):
        response = self.session.get(self.base_url + "/videos/1", headers=self.headers)
        assert response.status_code == 200
