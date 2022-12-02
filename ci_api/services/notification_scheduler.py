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
    """Return viewed today complexes list"""

    query = (
        select(ViewedComplex.user_id)
        .where(
            extract('day', ViewedComplex.viewed_at) == today.day
        )
    )
    return await _execute_all(session, query)


async def _get_users_with_notifications(
        session: AsyncSession, users_ids_for_notificate: list[int]
) -> list[int]:
    """Return user IDs list who need to create or update notifications"""

    query = (
        select(User.id)
        .join(Notification)
        .where(Notification.user_id.in_(users_ids_for_notificate))
    )
    return await _execute_all(session, query)


async def _get_notifications_for_create(users: list[int]) -> list[Notification]:
    """Return notifications list for users without notifications"""

    return [
        Notification(user_id=user, created_at=today, text=text)
        for user in users
    ]


async def _get_notifications_for_update(
        session: AsyncSession,
        users: list[int]
) -> list[Notification]:
    """Return updated notifications list without add to database"""

    for_update: list[Notification] = []
    for user in users:
        notifications: list = await Notification.get_all_by_user_id(session, user)
        for notification in notifications:
            notification.text = text
            notification.created_at = today
            for_update.append(notification)

    return for_update


async def create_and_update_notifications(
        session: AsyncSession, notifications: list[Notification]
) -> None:
    """Add notifications to database"""

    session.add_all(notifications)
    await session.commit()


async def _execute_all(session: AsyncSession, query):
    """Return all query results"""

    response = await session.execute(query)
    return response.scalars().all()


async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    async for session in get_db_session():

        today_viewed: list[ViewedComplex] = await _get_today_viewed_complexes(session)
        logger.debug(f"{today_viewed=}")

        users_ids_for_notification: list[int] = await _get_users_for_notification(
            session, today_viewed
        )
        logger.debug(f"Create notifications for next users, count: {len(users_ids_for_notification)}: "
                    f"\n{users_ids_for_notification}")

        users_for_update: list[int] = await _get_users_with_notifications(
            session, users_ids_for_notification
        )
        logger.debug(f"users_ids_for_notification: {users_for_update}")

        users_for_create: list[int] = [
            user_id
            for user_id in users_ids_for_notification
            if user_id not in users_for_update
        ]
        notifications_for_create: list[Notification] = await _get_notifications_for_create(
            users_for_create
        )

        notifications_for_update: list[Notification] = await _get_notifications_for_update(
            session, users_for_update
        )
        notifications_for_update.extend(notifications_for_create)

        await create_and_update_notifications(session, notifications_for_update)


if __name__ == '__main__':
    asyncio.run(create_notifications_for_not_viewed_users())


