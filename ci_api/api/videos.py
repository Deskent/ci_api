from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from config import settings, logger
from models.models import Video, User
from schemas.complexes_videos import VideoViewed
from services.depends import is_user_active
from services.response_manager import WebContext, ApiServiceResponser
from services.videos_methods import get_viewed_video_response

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
    logger.debug(f"Video requested: {video_id}")
    video: Video = await Video.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    full_path: Path = settings.MEDIA_DIR / video.file_name
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {video.file_name} not found")
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')


@router.post("/viewed", status_code=status.HTTP_200_OK, response_model=dict)
async def viewed_video(
        data: VideoViewed = Depends(VideoViewed.as_form),
):
    user: User = await User.get_by_phone(data.phone)
    web_context: WebContext = await get_viewed_video_response(
        user=user, video_id=data.video_id, context={}
    )

    return ApiServiceResponser(web_context).render()
