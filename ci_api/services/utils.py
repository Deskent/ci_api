import shutil
import subprocess
from datetime import time
from pathlib import Path

from fastapi import UploadFile, status, HTTPException

from config import settings
from database.db import engine, sessionmaker, AsyncSession
from models.models import Video


async def get_data_for_update(data: dict) -> dict:
    """Returns dictionary excluded None values"""

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }


def save_video(path: str, file: UploadFile):
    """Save video by path"""

    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f'File saved to {path}')


def _convert_string_to_time(data: str) -> time:
    """Convert string like xx.xxxxxx to time format"""
    datalist: list[int] = [int(elem) for elem in data.strip().split('.')]
    microsecond: int = datalist[1]
    second: int = datalist[0]
    hour: int = second // 3600
    minute: int = second // 60
    second %= 60

    return time(hour, minute, second, microsecond)


def get_video_duration(video_path: str) -> time:
    """Calculate video file duration"""

    result = subprocess.run(
        [
            'ffprobe',
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    if result.returncode == 0:
        return _convert_string_to_time(result.stdout.decode())

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f'Duration calculation error'
    )


async def upload_file(
        file_name: str,
        name: str,
        description: str,
        complex_id: int,
        file: UploadFile
) -> Video:
    """Check max videos in complex. Check video format. Save video file.
    Calculate video duration. Save row to database."""

    async_session = sessionmaker(
        engine, class_=AsyncSession
    )
    async with async_session() as session:
        videos: list[Video] = await Video.get_all_complex_videos(session, complex_id)
        if len(videos) >= 10:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="There is maximum video in this complex")
        if file.content_type != 'video/mp4':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f'Unsupported type {file.content_type}. Must be mp4.'
            )
        full_filename: str = f'{file_name}.mp4'
        file_path: Path = settings.MEDIA_DIR / full_filename
        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'File with name {full_filename} exists.'
            )
        save_video(str(file_path), file)
        duration: time = get_video_duration(str(file_path))
        video = Video(
            file_name=full_filename, description=description, name=name,
            complex_id=complex_id, duration=duration)
        session.add(video)
        await session.commit()

        return video
