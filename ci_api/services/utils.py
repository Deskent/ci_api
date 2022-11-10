import shutil

from fastapi import UploadFile


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
