import pytest

from database.db import get_db_session
from models.models import Complex, Video


@pytest.fixture
def get_complex_data() -> dict:
    return {
               "description": "Описание комплекса 1",
               "name": "комплекс 1",
               "number": 999,
               "next_complex_id": 2,
               "duration": 0
           }


@pytest.fixture
def get_video_data() -> dict:
    return {
               "description": "Описание тестового видео",
               "name": "тест видео 1",
               "file_name": "test_filename",
               "complex_id": 1,
               "duration": 30
           }


@pytest.mark.asyncio
async def test_add_complex(get_complex_data):
    async for session in get_db_session():
        new_complex = await Complex.add_new(session=session, **get_complex_data)
        assert new_complex.id
        await new_complex.delete(session=session)


@pytest.mark.asyncio
async def test_add_video(get_video_data):
    async for session in get_db_session():
        new_video = await Video.add_new(session=session, **get_video_data)
        assert new_video.id
        await new_video.delete(session=session)
