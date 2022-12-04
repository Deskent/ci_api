from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.responses import FileResponse

from config import settings, logger
from models.models import Video, User
from schemas.complexes_videos import VideoViewed
from services.depends import is_user_active, get_logged_user

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


@router.post("/viewed", status_code=status.HTTP_200_OK)
async def viewed_video(
        video_id: VideoViewed = Body(...),
        user: User = Depends(get_logged_user)
):
    result = {}
    logger.debug(f"VIEWED: {user} {video_id}")
    video: Video = await Video.get_by_id(video_id.video_id)
    if video:
        next_video = await video.next_video_id()
        if next_video:
            result.update(next_video=next_video, user=user)

    return result
