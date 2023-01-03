import pytest

from config import settings
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


@pytest.fixture
def create_video_file():
    file_path = settings.MEDIA_DIR / 'e1c1.mp4'
    created = False
    if not file_path.exists():
        created = True
        file_path.write_text('test')
    yield
    if created:
        file_path.unlink(missing_ok=True)


class TestVideo(BaseTest):

    @pytest.mark.server
    def test_all_videos_for_complex_id(self, event_loop):
        response = self.session.get(self.base_url + "/videos/all_for/1", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    @pytest.mark.manual
    def test_get_video_by_id(self, event_loop, create_video_file):
        response = self.session.get(self.base_url + "/complex/1/", headers=self.headers)
        assert response.status_code == 200
        complex_: dict = response.json()
        videos: list[dict] = complex_['videos']
        assert videos is not None
        video_id: int = videos[0].get('id')
        assert video_id is not None
        response = self.session.get(self.base_url + f"/videos/{video_id}/", headers=self.headers)
        assert response.status_code == 200
