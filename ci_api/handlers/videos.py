from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from config import MEDIA_DIR, logger
from database.db import get_session
from models.models import Video
from services.depends import is_user_active

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get("/{video_id}", dependencies=[Depends(is_user_active)])
async def get_video(
        video_id: int,
        session: AsyncSession = Depends(get_session)):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """
    logger.debug(f"Video requested: {video_id}")
    video: Video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    full_path: Path = MEDIA_DIR / video.file_name
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {video.file_name} not found")
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')


# @router.get("/", response_model=list[Video])
# async def get_videos(session: AsyncSession = Depends(get_session)):
#     """Get all videos
#
#     :return: List of Videos
#     """
#
#     result = await session.execute(select(Video))
#     return result.scalars().all()



