import pytest
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestVideo(BaseTest):

    @pytest.mark.server
    def test_all_videos_for_complex_id(self):
        response = self.session.get(self.base_url + "/videos/all_for/1", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

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
