import pytest
import requests


class TestVideos:
    @pytest.fixture()
    def setUp(self, base_url, user_create, user_payload):
        response = requests.post(base_url + "/auth/register", json=user_create)
        assert response.status_code == 200
        response = requests.post(base_url + "/auth/login", json=user_payload)
        assert response.status_code == 200
        token = response.json().get('token')

        headers = {'Authorization': f"Bearer {token}"}
        yield headers
        response = requests.delete(base_url + "/users", headers=headers)
        assert response.status_code == 204

    def test_get_video_by_id(self, setUp, get_bearer, base_url):
        response = requests.get(base_url + "/videos/1", headers=setUp)
        assert response.status_code == 200
