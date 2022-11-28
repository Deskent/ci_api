from datetime import time

from loguru import logger

from config import logger


@logger.catch
async def get_data_for_update(data: dict) -> dict:
    """Returns dictionary excluded None values"""

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }


@logger.catch
def convert_seconds_to_time(data: int) -> time:
    """Convert integer seconds to datetime.time format"""

    if not data:
        return time(0, 0, 0)

    hour: int = data // 3600
    minute: int = data // 60
    second: int = data % 60

    return time(hour, minute, second)
