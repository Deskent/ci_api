from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from database.db import get_session
from models.models import Notification, User
from schemas.notifications import NotificationBase, NotificationUpdate
from services.depends import get_logged_user
from services.utils import get_data_for_update

router = APIRouter(prefix="/notifications", tags=['Notifications'])


@router.post("/", response_model=NotificationUpdate)
async def create_notification(
        data: NotificationBase,
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """Create notification for user by user database id

    :param notification_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :return: Notification created information as JSON
    """

    notification: Notification = Notification(**data.dict(), user_id=user.id)
    session.add(notification)
    await session.commit()
    logger.info(f"Notification with id {notification.id} created")

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationUpdate
)
async def get_notification(
        notification_id: int,
        session: AsyncSession = Depends(get_session),
        user: User = Depends(get_logged_user)
):
    notification = await session.get(Notification, notification_id)
    if notification and notification.user_id == user.id:
        return notification
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.put(
    "/{notification_id}",
    response_model=NotificationUpdate,
    dependencies=[Depends(get_logged_user)]
)
async def update_notification(
        notification_id: int,
        data: NotificationBase,
        session: AsyncSession = Depends(get_session)
):
    """
    Update notification by id. Need authorization.

    :param notification_id: integer Notification id in database

    :param notification_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :return: Notification updated information as JSON
    """

    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    updated_data: dict = await get_data_for_update(data.dict())
    query = update(Notification).where(Notification.id == notification_id).values(**updated_data)
    await session.execute(query)
    session.add(notification)
    await session.commit()
    logger.info(f"Notification with id {notification_id} updated")

    return notification


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_logged_user)]
)
async def delete_notification(
        notification_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Delete notification by its id. Need authorization.

    :param notification_id: integer - Notification id in database

    :return: None
    """
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await session.delete(notification)
    await session.commit()

    logger.info(f"Notification with id {notification_id} deleted")
