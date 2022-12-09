from pathlib import Path

from fastapi import APIRouter, Depends, status, Body
from fastapi.responses import FileResponse

from config import settings, logger
from models.models import Video, User
from schemas.complexes_videos import VideoViewed
from schemas.user_schema import slice_phone_to_format
from services.depends import is_user_active
from services.response_manager import WebContext, ApiServiceResponser
from services.videos_methods import get_viewed_video_response
from web_service.utils.web_utils import get_checked_video

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get("/{video_id}", dependencies=[Depends(is_user_active)])
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


@router.post("/viewed", status_code=status.HTTP_200_OK, response_model=dict)
async def video_viewed(
        data: VideoViewed
):
    phone: str = slice_phone_to_format(data.phone)
    user: User = await User.get_by_phone(phone)
    web_context: WebContext = await get_viewed_video_response(
        user=user, video_id=data.video_id, context={}
    )

    return ApiServiceResponser(web_context).render()
