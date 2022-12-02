import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlmodel.ext.asyncio.session import AsyncSession

from config import logger
from database.db import get_db_session
from models.models import User, ViewedComplex, Notification


today = datetime.today()
text = "Зарядка не выполнена, не забудьте выполнить упражнения"


async def _get_users_for_notification(
        session: AsyncSession, today_viewed: list[ViewedComplex]
) -> list[int]:
    query = select(User.id).where(User.is_verified == True).filter(User.id.not_in(today_viewed))

    return await _execute_all(session, query)


async def _get_today_viewed_complexes(session: AsyncSession) -> list[ViewedComplex]:

    query = (
        select(ViewedComplex.user_id)
        .where(
            extract('day', ViewedComplex.viewed_at) == today.day
        )
    )
    return await _execute_all(session, query)


async def _create_notifications(session: AsyncSession, users: list[int]) -> None:
    """Create notifications for user not viewed complex today"""

    notifications = [
        Notification(user_id=user, created_at=today, text=text)
        for user in users
    ]
    session.add_all(notifications)
    await session.commit()


async def _get_users_with_notifications(
        session: AsyncSession, users_ids_for_notificate: list[int]
) -> list[int]:
    query = (
        select(User.id)
        .join(Notification)
        .where(Notification.user_id.in_(users_ids_for_notificate))
    )
    return await _execute_all(session, query)


async def _update_notifications(session: AsyncSession, users: list[int]) -> None:
    """Create notifications for user not viewed complex today"""

    for_update: list[Notification] = []
    for user in users:
        notifications: list = await Notification.get_all_by_user_id(session, user)
        for notification in notifications:
            notification.text = text
            notification.created_at = today
            for_update.append(notification)

    session.add_all(for_update)
    await session.commit()


async def _execute_all(session: AsyncSession, query):
    response = await session.execute(query)
    return response.scalars().all()


async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    async for session in get_db_session():

        today_viewed: list[ViewedComplex] = await _get_today_viewed_complexes(session)
        logger.debug(f"{today_viewed=}")

        users_ids_for_notificate: list[int] = await _get_users_for_notification(session, today_viewed)
        logger.debug(f"Create notifications for next users, count: {len(users_ids_for_notificate)}: "
                    f"\n{users_ids_for_notificate}")

        users_for_update: list[int] = await _get_users_with_notifications(
            session, users_ids_for_notificate
        )
        logger.debug(f"users_ids_for_notificate: {users_for_update}")

        users_for_create = [
            user
            for user in users_ids_for_notificate
            if user not in users_for_update
        ]

        await _create_notifications(session, users_for_create)
        await _update_notifications(session, users_for_update)


if __name__ == '__main__':
    asyncio.run(create_notifications_for_not_viewed_users())
