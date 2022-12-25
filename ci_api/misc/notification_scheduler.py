from datetime import datetime

from config import logger
from crud_class.crud import CRUD
from database.models import ViewedComplex, Notification
from misc.notification_sender import send_push_messages

today = datetime.today()
message_text = "Зарядка не выполнена, не забудьте выполнить упражнения"


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


async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    users_ids_for_notification: list[int] = await CRUD.user.get_users_ids_for_create_notifications()
    logger.info(
        f"Create notifications for next users [{len(users_ids_for_notification)}]: "
        f"\n{users_ids_for_notification}"
    )

    users_for_update: list[int] = await CRUD.user.get_users_have_notification(
        users_ids_for_notification
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

    notifications_for_update: list[
        Notification] = await _get_notifications_for_update(users_for_update)
    notifications_for_update.extend(notifications_for_create)

    await CRUD.notification.create_and_update_notifications(notifications_for_update)
    user_tokens: list[str] = await CRUD.user.get_tokens_for_send_notification_push()
    logger.info(f"Tokens for pushing messages [{len(user_tokens)}]: {user_tokens}")
    result: list = await send_push_messages(message=message_text, tokens=user_tokens)
    logger.info(f"Notifications send: [{len(result)}]")
