
import pytest
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestUsers(BaseTest):

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
    def test_login_endpoint_wrong_password(self):
        payload = {
            "phone": self.user_create.phone,
            "password": "wrong_password"

        }
        response = self.session.post(self.base_url + "/auth/login", json=payload)
        assert response.status_code == 404

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

    @pytest.mark.server
    def test_get_rates(self):
        response = self.session.get(self.base_url + "/users/rates", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.server
    def test_edit_user_profile(self):
        new_username = "new_test_name"
        new_third_name = "new_third_name"
        payload = {
            "username": new_username,
            "third_name": new_third_name
        }
        response = self.session.put(
            self.base_url + "/users/edit", headers=self.headers, json=payload
        )
        assert response.status_code == 200
        data: dict = response.json()
        assert data.get('username') == new_username
        assert data.get('third_name') == new_third_name

    @pytest.mark.skip("Need to know verify code from database")
    def test_verify_email(self):
        url = self.base_url + "/auth/verify_email" + f"?token={self.email_token}"
        response = self.session.get(url)
        assert response.status_code == 202
