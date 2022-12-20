from crud_class.crud import CRUD
from models.models import Complex, Video


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
    created_video = await CRUD.video.save(video)
    assert created_video.id > 0


async def test_get_video_by_id():
    all_videos: list[Video] = await CRUD.video.get_all()
    last_video: Video = max(all_videos, key=lambda x: x.id)
    data: Video = await CRUD.video.get_by_id(last_video.id)
    assert data is not None


async def test_video_update():
    all_videos: list[Video] = await CRUD.video.get_all()
    last_video: Video = max(all_videos, key=lambda x: x.id)
    data: Video = await CRUD.video.get_by_id(last_video.id)
    assert data.duration == 99
    data.duration = 100
    new_data: Complex = await CRUD.video.save(data)
    assert new_data.duration == 100


async def test_get_next_video():
    video: Video = await CRUD.video.get_by_id(1)
    next_video: int = await CRUD.video.next_video_id(video)
    assert next_video == 2


async def test_get_videos_duration():
    all_videos: list[Video] = await CRUD.video.get_all()
    videos_ids: tuple[int] = tuple(int(elem.id) for elem in all_videos)
    duration: int = await CRUD.video.get_videos_duration(videos_ids)
    assert duration > 0


async def test_get_videos_ordered_list():
    next_video: list[Video] = await CRUD.video.get_ordered_list(1)
    assert len(next_video) > 0


async def test_get_videos_by_complex_id():
    next_video: list[Video] = await CRUD.video.get_all_by_complex_id(1)
    assert len(next_video) > 0


async def test_video_delete():
    all_videos: list[Video] = await CRUD.video.get_all()
    last_id: Video = max(all_videos, key=lambda x: x.id)
    await CRUD.video.delete_by_id(last_id.id)

