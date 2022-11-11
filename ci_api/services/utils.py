import shutil
import subprocess
from datetime import time

from fastapi import UploadFile, status, HTTPException


async def get_data_for_update(data: dict) -> dict:
    """Returns dictionary excluded None values"""

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }


def save_video(path: str, file: UploadFile):
    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f'File saved to {path}')


def _convert_string_to_time(data: str) -> time:
    datalist: list[int] = [int(elem) for elem in data.strip().split('.')]
    microsecond: int = datalist[1]
    second: int = datalist[0]
    hour: int = second // 3600
    minute: int = second // 60
    second %= 60

    return time(hour, minute, second, microsecond)


def get_video_duration(input_video: str) -> time:
    result = subprocess.run(
        [
            'ffprobe',
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            input_video
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    if result.returncode == 0:
        return _convert_string_to_time(result.stdout.decode())

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f'Duration calculation error'
    )
