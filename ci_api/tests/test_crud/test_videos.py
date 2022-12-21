from crud_class.crud import CRUD
from database.models import Video



async def test_get_video_by_id(get_video):
    data: Video = await CRUD.video.get_by_id(get_video.id)
    assert data is not None


async def test_video_update(get_video):
    data: Video = await CRUD.video.get_by_id(get_video.id)
    assert data.duration == 99
    data.duration = 100
    new_data: Video = await CRUD.video.save(data)
    assert new_data.duration == 100


async def test_get_next_video(get_video):
    video: Video = await CRUD.video.get_by_id(get_video.id)
    next_video: int = await CRUD.video.next_video_id(video)
    assert next_video > 0


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


async def test_get_hello_video():
    video: Video = await CRUD.video.get_hello_video()
    assert video.id > 0
