import shutil
import subprocess
from pathlib import Path

from fastapi import UploadFile, HTTPException
from loguru import logger
from starlette import status

from config import MAX_VIDEO, settings
from database.models import Video, Complex, Administrator
from schemas.complexes_videos import VideoUpload
from crud_class.crud import CRUD


@logger.catch
def save_uploaded_file(file_path: str, file: UploadFile):
    """Save file by path"""

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f'Uploaded file saved to {file_path}')


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

    current_complex: Complex = await CRUD.complex.get_by_id(file_form.complex_id)
    if not current_complex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complex with id {file_form.complex_id} not found")

    videos: list[Video] = await CRUD.video.get_all_by_complex_id(current_complex.id)
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
    save_uploaded_file(str(file_path), file_form.file)

    duration: int = get_video_duration(str(file_path))
    file_form.duration = duration
    file_form.file_name = full_filename

    data: dict = file_form.dict()
    del data['file']
    # REFACTORED 18 dec 23:41
    video = await CRUD.video.create(data)

    logger.info(f"Video {file_form.file_name} for complex {file_form.complex_id} uploaded.")

    return video


async def create_default_admin() -> None:
    admins: list[Administrator] = await CRUD.admin.get_all()

    if not admins and settings.CREATE_ADMIN:
        logger.warning("No admins found. Creating new admin.")

        data = []
        if settings.DEFAULT_ADMIN:
            data.append(settings.DEFAULT_ADMIN)

        for elem in data:
            await CRUD.admin.create(elem)
        logger.info("Admin created.")
