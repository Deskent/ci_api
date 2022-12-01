import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlmodel.ext.asyncio.session import AsyncSession

from config import logger
from database.db import get_db_session
from models.models import User, ViewedComplex, Notification


today = datetime.today()


async def _get_users_for_notification(
        session: AsyncSession, today_viewed: list[ViewedComplex]
) -> list[User]:
    query = select(User).where(User.is_verified == True).filter(User.id.not_in(today_viewed))

    return await _execute_all(session, query)


async def _get_today_viewed_complexes(session: AsyncSession) -> list[ViewedComplex]:

    query = (
        select(ViewedComplex.user_id)
        .where(
            extract('day', ViewedComplex.viewed_at) == today.day
        )
    )
    return await _execute_all(session, query)


async def _create_notifications(session: AsyncSession, users: list[User]) -> None:
    """Create notifications for user not viewed complex today"""

    text = "Зарядка не выполнена, не забудьте выполнить упражнения"

    notifications = [
        Notification(user_id=user.id, created_at=today, text=text)
        for user in users
    ]
    session.add_all(notifications)
    await session.commit()


async def _execute_all(session: AsyncSession, query):
    response = await session.execute(query)
    return response.scalars().all()


async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    async for session in get_db_session():

        today_viewed: list[ViewedComplex] = await _get_today_viewed_complexes(session)
        logger.info(today_viewed)

        user_need_to_notificate = await _get_users_for_notification(session, today_viewed)
        logger.info(f"Create notifications for next users {len(user_need_to_notificate)}: "
                    f"\n{user_need_to_notificate}")

        await _create_notifications(session, user_need_to_notificate)


if __name__ == '__main__':
    asyncio.run(create_notifications_for_not_viewed_users())
