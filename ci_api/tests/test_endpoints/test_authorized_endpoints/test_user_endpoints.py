from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestUsers(BaseTest):

    def test_get_me(self):
        response = self.session.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        user_id = data.get("email")
        assert user_id is not None
        assert data.get('max_level') is not None
        self.user_id = user_id

    def test_login_endpoint(self):
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    def test_login_endpoint_wrong_password(self):
        payload = {
            "phone": self.user_create.phone,
            "password": "wrong_password"

        }
        response = self.session.post(self.base_url + "/auth/login", json=payload)
        assert response.status_code == 404

    def test_change_password(self):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = self.session.put(
            self.base_url + "/users/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202

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
