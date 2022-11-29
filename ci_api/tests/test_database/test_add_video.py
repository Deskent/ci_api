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


async def test_add_video(db_session, get_video_data):
    new_video = await Video.add_new(session=db_session, **get_video_data)

    assert new_video.id
    await new_video.delete(session=db_session)


import pytest

from models.models import Complex


@pytest.fixture
def get_complex_data() -> dict:
    return {
               "description": "Описание комплекса 1",
               "name": "комплекс 1",
               "number": 999,
               "next_complex_id": 2,
               "duration": 0
           }


async def test_add_complex(db_session, get_complex_data):
    new_complex = await Complex.add_new(session=db_session, **get_complex_data)
    assert new_complex.id
    await new_complex.delete(session=db_session)
