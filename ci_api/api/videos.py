from pathlib import Path

from fastapi import APIRouter, status, Depends
from fastapi.responses import FileResponse

from config import settings, logger
from database.models import Video
from services.depends import get_logged_user
from crud_class.crud import CRUD
from web_service.utils.web_utils import get_checked_video

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get(
    "/{video_id}",
    dependencies=[Depends(get_logged_user)],
    status_code=status.HTTP_200_OK
)
async def get_video(
        video_id: int,
):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """

    video: Video = await get_checked_video(video_id)
    full_path: Path = settings.MEDIA_DIR / video.file_name
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')


@router.get(
    "/all_for/{complex_id}",
    dependencies=[Depends(get_logged_user)],
    response_model=list[Video],
    status_code=status.HTTP_200_OK
)
async def get_all_videos_from_complex(
        complex_id: int
):
    """
    Return list videos by complex id. Need active user.

    :param complex_id: int - Complex database ID

    :return: List of videos as JSON

    """
    return await CRUD.video.get_all_by_complex_id(complex_id)
