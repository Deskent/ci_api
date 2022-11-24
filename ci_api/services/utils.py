from config import logger


@logger.catch
async def get_data_for_update(data: dict) -> dict:
    """Returns dictionary excluded None values"""

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }
