from fastapi import APIRouter, status, Depends, Header

from config import logger, site
from crud_class.crud import CRUD
from database.models import Video
from services.depends import get_logged_user

CHUNK_SIZE = 1024 * 1024

router = APIRouter(prefix="/videos", tags=['Videos'])


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
