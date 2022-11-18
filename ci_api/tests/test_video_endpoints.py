# import pytest
#
#
# class TestVideos:
#     @pytest.fixture()
#     def setUp(self, test_app, base_url, user_create, user_payload):
#         self.session = test_app
#         response = self.session.post(base_url + "/auth/register", json=user_create)
#         assert response.status_code == 200
#         response = self.session.post(base_url + "/auth/login", json=user_payload)
#         assert response.status_code == 200
#         token = response.json().get('token')
#
#         headers = {'Authorization': f"Bearer {token}"}
#         yield headers
#         response = self.session.delete(base_url + "/users", headers=headers)
#         assert response.status_code == 204
#
