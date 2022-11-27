import shutil
import subprocess
from datetime import time, datetime, timedelta
from pathlib import Path

from fastapi import UploadFile, HTTPException
from loguru import logger
from sqlalchemy import select
from starlette import status

from config import MAX_VIDEO, settings
from database.db import get_db_session
from models.models import Video, Complex, Administrator
from schemas.complexes_videos import VideoUpload


@logger.catch
def save_video(path: str, file: UploadFile):
    """Save video by path"""

    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f'Video file saved to {path}')


@logger.catch
def convert_seconds_to_time(data: int) -> time:
    """Convert integer seconds to datetime.time format"""

    if not data:
        return time(0, 0, 0)

    hour: int = data // 3600
    minute: int = data // 60
    second: int = data % 60

    return time(hour, minute, second)


def get_video_duration(video_path: str) -> int:
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
        return int(float(result.stdout.decode()))

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f'Duration calculation error'
    )


async def upload_file(
        file_form: VideoUpload
) -> Video:
    """Check max videos in complex. Check video format. Save video file.
    Calculate video duration. Save row to database."""

    async for session in get_db_session():
        current_complex: Complex = await session.get(Complex, file_form.complex_id)
        if not current_complex:
            logger.warning(f"Complex {file_form.complex_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Complex with id {file_form.complex_id} not found")
        query = select(Video).where(Video.complex_id == current_complex.id)
        videos_row = await session.execute(query)
        videos: list[Video] = videos_row.scalars().all()
        if len(videos) >= MAX_VIDEO:
            logger.warning(f"For complex {file_form.complex_id} exists {MAX_VIDEO} videos")
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="There is maximum video in this complex")
        if file_form.file.content_type != 'video/mp4':
            logger.warning(f'Unsupported type {file_form.file.content_type}')
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f'Unsupported type {file_form.file.content_type}. Must be mp4.'
            )
        full_filename: str = f'{file_form.file_name}.mp4'
        file_path: Path = settings.MEDIA_DIR / full_filename
        if file_path.exists():
            error_text = f'File with name {full_filename} exists.'
            logger.warning(error_text)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_text
            )
        save_video(str(file_path), file_form.file)
        file_form.duration = get_video_duration(str(file_path))
        file_form.file_name = full_filename
        video = Video(**file_form.dict())
        session.add(video)
        await session.commit()

        current_complex.video_count += 1
        session.add(current_complex)
        await session.commit()

        logger.info(f"Video {file_form.file_name} for complex {current_complex.id} uploaded.")

        return video


async def create_default_admin() -> None:
    async for session in get_db_session():
        response = await session.execute(select(Administrator))
        admins: list[Administrator] = response.scalars().all()

        if not admins and settings.CREATE_ADMIN:
            logger.warning("No admins found. Creating new admin.")

            data = []
            if settings.DEFAULT_ADMIN:
                data.append(settings.DEFAULT_ADMIN)

            for elem in data:
                expired_at = datetime.utcnow() + timedelta(days=30)
                elem['password'] = await Administrator.get_hashed_password(elem['password'])
                user = Administrator(**elem, expired_at=expired_at)
                session.add(user)
            await session.commit()
            logger.info("Admin created.")
