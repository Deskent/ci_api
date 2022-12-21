import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.sql import extract

from config import logger
from crud_class.crud import CRUD
from database.models import User, ViewedComplex, Notification
from database.db import get_db_session, get_all

today = datetime.today()
message_text = "Зарядка не выполнена, не забудьте выполнить упражнения"


async def _get_users_for_notification(
        today_viewed: list[ViewedComplex]
) -> list[int]:
    query = (
        select(User.id)
        .where(User.is_verified == True and User.is_active == True)
        .filter(User.id.not_in(today_viewed))
    )

    return await get_all(query)


async def _get_today_viewed_complexes() -> list[ViewedComplex]:
    """Return viewed today complexes list"""

    query = (
        select(ViewedComplex.user_id)
        .where(
            extract('day', ViewedComplex.viewed_at) == today.day
        )
    )
    return await get_all(query)


async def _get_users_with_notifications(
        users_ids_for_notificate: list[int]
) -> list[int]:
    """Return user IDs list who need to create or update notifications"""

    query = (
        select(User.id)
        .join(Notification)
        .where(Notification.user_id.in_(users_ids_for_notificate))
    )
    return await get_all(query)


async def _get_notifications_for_create(users: list[int]) -> list[Notification]:
    """Return notifications list for users without notifications"""

    return [
        Notification(user_id=user, created_at=today, text=message_text)
        for user in users
    ]


async def _get_notifications_for_update(
        users: list[int]
) -> list[Notification]:
    """Return updated notifications list without add to database"""

    for_update: list[Notification] = []
    for user in users:
        notifications: list = await CRUD.notification.get_all_by_user_id(user)
        for notification in notifications:
            notification.text = message_text
            notification.created_at = today
            for_update.append(notification)

    return for_update


async def create_and_update_notifications(notifications: list[Notification]) -> None:
    """Add notifications to database"""

    async for session in get_db_session():
        session.add_all(notifications)
        await session.commit()


async def _get_tokens_from_with_notifications() -> list[str]:
    """Return list of user tokens user having notification"""

    query = select(User.push_token).join(Notification).where(User.push_token is not None)

    return await get_all(query)

async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    today_viewed: list[ViewedComplex] = await _get_today_viewed_complexes()
    logger.debug(f"{today_viewed=}")

    users_ids_for_notification: list[int] = await _get_users_for_notification(today_viewed)
    logger.debug(f"Create notifications for next users, count: {len(users_ids_for_notification)}: "
                f"\n{users_ids_for_notification}")

    users_for_update: list[int] = await _get_users_with_notifications(users_ids_for_notification)
    logger.debug(f"users_ids_for_notification: {users_for_update}")

    users_for_create: list[int] = [
        user_id
        for user_id in users_ids_for_notification
        if user_id not in users_for_update
    ]
    notifications_for_create: list[Notification] = await _get_notifications_for_create(
        users_for_create
    )

    notifications_for_update: list[Notification] = await _get_notifications_for_update(users_for_update)
    notifications_for_update.extend(notifications_for_create)

    await create_and_update_notifications(notifications_for_update)
    # user_tokens: list[str] = await _get_tokens_from_with_notifications()
    # await send_push_messages(message=message_text, tokens=user_tokens)

if __name__ == '__main__':
    asyncio.run(create_notifications_for_not_viewed_users())


