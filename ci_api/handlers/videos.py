from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from config import MEDIA_DIR
from database.db import get_session
from models.models import Video

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get("/{video_id}")
async def get_video(
        video_id: int,
        session: AsyncSession = Depends(get_session)):
    """

    """

    video: Video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    full_path: Path = MEDIA_DIR / video.file_name
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {video.file_name} not found")

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



