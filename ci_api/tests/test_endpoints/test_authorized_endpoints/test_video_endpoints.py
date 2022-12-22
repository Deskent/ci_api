import pytest

from crud_class.crud import CRUD
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestVideo(BaseTest):

    @pytest.mark.server
    def test_all_videos_for_complex_id(self):
        response = self.session.get(self.base_url + "/videos/all_for/1", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.server
    def test_get_video_by_id(self, event_loop):
        response = self.session.get(self.base_url + f"/complex/1/", headers=self.headers)
        assert response.status_code == 200
        complexes: dict = response.json()
        video_id: int = complexes['videos'][0].get('id')
        response = self.session.get(self.base_url + f"/videos/{video_id}/", headers=self.headers)
        assert response.status_code == 200
