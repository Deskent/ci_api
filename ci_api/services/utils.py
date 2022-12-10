import datetime
import random
import secrets
from datetime import time

from config import logger


def get_current_datetime() -> datetime:
    return datetime.datetime.now(tz=None)


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


def convert_to_minutes(data: int) -> int:
    return convert_seconds_to_time(data).minute


def generate_four_random_digits_string() -> str:
    return "".join(
        (str(random.randint(0, 9)) for _ in range(4))
    )


def represent_phone(phone: str) -> str:
    return f"8 ({phone[:3]}) {phone[3:6]}-{phone[6:]}"


def generate_random_password() -> str:
    return secrets.token_hex(8)


def to_isoformat(data: datetime.datetime) -> str:
    return data.replace(tzinfo=None).isoformat(sep=' ', timespec='seconds')
