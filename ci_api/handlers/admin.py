import datetime
from datetime import time
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, HTTPException, status, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import MEDIA_DIR
from database.db import get_session
from models.models import Video, User
from schemas.complexes_videos import VideoUpload
from services.utils import save_video, get_video_duration

router = APIRouter(tags=['Admin'])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_video(
        file_name: str,
        name: str,
        description: str,
        complex_id: int,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Upload video file in format mp4. FOr admin only.

    :param file_name: string - Name for file without file extension

    :param name: string - Name for video

    :param description: string - Description for video

    :param complex_id: int - Video complex id

    :param duration: string - Video duration in minutes in time
        format: HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :return: Video created data as JSON
    """
    video_data: VideoUpload = VideoUpload(
        file_name=file_name, name=name, description=description, complex_id=complex_id)

    if file.content_type != 'video/mp4':
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f'Unsupported type {file.content_type}. Must be mp4.'
        )
    full_filename: str = f'{video_data.file_name}.mp4'
    file_path: Path = MEDIA_DIR / full_filename
    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'File with name {full_filename} exists.'
        )
    save_video(str(file_path), file)
    duration: time = get_video_duration(str(file_path))
    video = Video(
        file_name=full_filename, description=video_data.description, name=video_data.name,
        complex_id=video_data.complex_id, duration=duration)
    session.add(video)
    await session.commit()

    return video


@router.get("/", response_model=list[User])
async def get_users(session: AsyncSession = Depends(get_session)):
    """
    Get all users from database. For admin only.

    :return: List of users as JSON
    """

    users = await session.execute(select(User).order_by(User.id))

    return users.scalars().all()
