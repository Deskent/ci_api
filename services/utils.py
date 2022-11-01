async def get_data_for_update(data: dict) -> dict:
    return {
        key: value
        for key, value in data.items()
        if value is not None
    }
