from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings, logger
from database.db import get_db_session
from models.models import Video
from services.depends import is_user_active

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get("/{video_id}", dependencies=[Depends(is_user_active)])
async def get_video(
        video_id: int,
        session: AsyncSession = Depends(get_db_session)):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """
    logger.debug(f"Video requested: {video_id}")
    video: Video = await Video.get_by_id(session, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    full_path: Path = settings.MEDIA_DIR / video.file_name
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {video.file_name} not found")
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')