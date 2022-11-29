import pytest

from models.models import Video


@pytest.fixture
def get_video_data() -> dict:
    return {
        "description": "Описание тестового видео",
        "name": "тест видео 1",
        "file_name": "test_filename",
        "complex_id": 1,
        "duration": 30
    }


@pytest.mark.skip
async def test_add_video(db_session, get_video_data):
    new_video = await Video.add_new(session=db_session, **get_video_data)

    assert new_video.id
    await new_video.delete(session=db_session)
