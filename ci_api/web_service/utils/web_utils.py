from pathlib import Path

from config import settings
from crud_class.crud import CRUD
from exc.exceptions import FileNotFoundError, VideoNotFoundError
from database.models import Video


async def get_checked_video(video_id: int) -> Video:
    video: Video = await CRUD.video.get_by_id(video_id)
    if not video:
        raise VideoNotFoundError
    file_path: Path = settings.MEDIA_DIR / video.file_name
    if file_path.exists():
        return video

    raise FileNotFoundError
