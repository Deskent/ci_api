import asyncio
from datetime import datetime

from alembic.operations.toimpl import bulk_insert
from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlmodel.ext.asyncio.session import AsyncSession

from database.db import get_db_session
from models.models import User, ViewedComplex, Notification
from config import settings, logger


async def get_users_for_notification():
    return None


async def _execute_all(session: AsyncSession, query):
    response = await session.execute(query)
    return response.scalars().all()


async def send_notifications():
    """Create notifications for user not viewed complex today"""

    today = datetime.today()
    async for session in get_db_session():
        query = (
            select(ViewedComplex.user_id)
            .where(
                extract('day', ViewedComplex.viewed_at) == today.day
            )
        )
        today_viewed = await _execute_all(session, query)
        logger.info(today_viewed)

        query = select(User).filter(User.id.not_in(today_viewed))
        user_need_to_notificate = await _execute_all(session, query)
        logger.info(f"Create notifications for next users {len(user_need_to_notificate)}: "
                    f"\n{user_need_to_notificate}")
        text = "Зарядка не выполнена, не забудьте выполнить упражнения"

        notifications = [
            Notification(user_id=user.id, created_at=today, text=text)
            for user in user_need_to_notificate
        ]
        session.add_all(notifications)
        await session.commit()


if __name__ == '__main__':
    asyncio.run(send_notifications())
