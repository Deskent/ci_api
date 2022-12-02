from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from database.db import get_db_session
from models.models import Notification, User
from schemas.notifications import NotificationUpdate
from services.depends import get_logged_user

router = APIRouter(prefix="/notifications", tags=['Notifications'])


@router.get(
    "/{notification_id}",
    response_model=NotificationUpdate
)
async def get_notification(
        notification_id: int,
        session: AsyncSession = Depends(get_db_session),
        user: User = Depends(get_logged_user)
):
    """Get notification by its id. Need authorization.

    :param notification_id: integer - Notification id in database

    :return: Notification data as JSON
    """
    notification = await Notification.get_by_id(session, notification_id)
    if notification and notification.user_id == user.id:
        return notification
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_logged_user)]
)
async def delete_notification(
        notification_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    """Delete notification by its id. Need authorization.

    :param notification_id: integer - Notification id in database

    :return: None
    """
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await notification.delete(session)

    logger.info(f"Notification with id {notification_id} deleted")
