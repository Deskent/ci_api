import datetime
from pathlib import Path

from fastapi import APIRouter, status, Depends, Header
from fastapi.responses import FileResponse

from config import settings, logger, site
from crud_class.crud import CRUD
from database.models import Video
from services.depends import get_logged_user
from web_service.utils.web_utils import get_checked_video

CHUNK_SIZE = 1024 * 1024

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
    logger.debug(f"Temporary path: {full_path}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')


@router.get(
    "/all_for/{complex_id}",
    dependencies=[Depends(get_logged_user)],
    response_model=list[Video],
    status_code=status.HTTP_200_OK
)
async def get_all_videos_from_complex(
        complex_id: int,
        user_agent: str = Header(...)
):
    """
    Return list videos by complex id. Need active user.

    :param complex_id: int - Complex database ID

    :return: List of videos as JSON

    """
    logger.info(f'User Agent: {user_agent}')
    videos: list[Video] = await CRUD.video.get_all_by_complex_id(complex_id)

    result = videos[:]
    for video in result:
        video.file_name = site.SITE_URL + '/media/' + video.file_name

    return result


@router.get(
    "/temp_video/{video_id}",
    dependencies=[Depends(get_logged_user)],
    status_code=status.HTTP_200_OK
)
async def get_video_with_random_key(
        video_id: int,
):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """

    video: Video = await get_checked_video(video_id)
    key: str = str(int(datetime.datetime.utcnow().timestamp()))
    temporary_path: Path = settings.MEDIA_DIR / key
    temporary_path.mkdir(parents=True)
    full_path: Path = temporary_path / video.file_name
    logger.debug(f"Temporary path: {full_path}:  OK")
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')
