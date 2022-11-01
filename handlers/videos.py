import os.path
import shutil

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, HTTPException, status, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db import get_session
from models.models import *


videos_router = APIRouter()
TAGS = ['Videos']


def save_video(path: str, file: UploadFile):
    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)


@videos_router.get("/", response_model=list[Video], tags=TAGS)
async def get_videos(session: AsyncSession = Depends(get_session)):
    """Get all videos

    :return: List of Videos
    """

    result = await session.execute(select(Video))
    return result.scalars().all()


@videos_router.post("/", response_model=Video, tags=TAGS)
async def add_video(
        tasks: BackgroundTasks,
        name: str,
        description: str,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Upload video file in format mp4

    :param name: Name for file

    :param description: Description for video

    :return: Video created data as JSON
    """

    if file.content_type != 'video/mp4':
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f'Unsupported type {file.content_type}. Must be mp4.'
        )
    path = f'media/{name}.mp4'
    if os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'File with name {name} exists.'
        )
    tasks.add_task(save_video, path, file)

    video = Video(path=path, description=description, name=name, next_id=0)
    session.add(video)
    await session.commit()

    return video
