import asyncio
import datetime

from database.db import get_db_session
from models.models import User
from config import settings, logger


async def get_users_for_notification():
    return None


async def send_notifications():
    # async for session in get_db_session():
    #     if not await ApplicationInfo.is_last_check_today(session):
    #         users: list[User] = await get_users_for_notification()
    logger.info("SENDING NOTIFICATIONS")
