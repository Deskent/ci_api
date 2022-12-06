import pytest

from models.models import Complex, Video
from models.methods import get_first, select, get_all


async def test_video_create():
    data = {
        "description": "Описание video 99",
        "name": "video 99",
        "number": 99,
        "duration": 99,
        "complex_id": 1,
        "file_name": "text_name.mp4"
    }
    video: Video = Video(**data)
    created_video = await video.save()
    assert created_video.id > 0


async def test_get_video_by_id():
    all_videos: list[Video] = await Video.get_all()
    last_video: Video = max(all_videos, key=lambda x: x.id)
    data: Video = await Video.get_by_id(last_video.id)
    assert data is not None


async def test_video_update():
    all_videos: list[Video] = await Video.get_all()
    last_video: Video = max(all_videos, key=lambda x: x.id)
    data: Video = await Video.get_by_id(last_video.id)
    assert data.duration == 99
    data.duration = 100
    new_data: Complex = await data.save()
    assert new_data.duration == 100


async def test_get_next_video():
    data: Video = await Video.get_by_id(1)
    next_video: int = await data.next_video_id()
    assert next_video == 2


async def test_get_videos_duration():
    all_videos: list[Video] = await Video().get_all()
    videos_ids: tuple[int] = tuple(int(elem.id) for elem in all_videos)
    duration: int = await Video().get_videos_duration(videos_ids)
    assert duration > 0


async def test_get_videos_ordered_list():
    next_video: list[Video] = await Video.get_ordered_list(1)
    assert len(next_video) > 0


async def test_get_videos_by_complex_id():
    next_video: list[Video] = await Video.get_all_by_complex_id(1)
    assert len(next_video) > 0


async def test_video_delete():
    all_videos: list[Video] = await Video.get_all()
    last_id: Video = max(all_videos, key=lambda x: x.id)
    await Video.delete_by_id(last_id.id)

