from fastapi import APIRouter, Depends, status

from config import logger
from crud_class.crud import CRUD
from exc.exceptions import NotificationNotFound
from database.models import Notification, User
from schemas.notifications import NotificationUpdate, NotificationCreate
from services.depends import get_logged_user

router = APIRouter(prefix="/notifications", tags=['Notifications'])


@router.post(
    "/",
    response_model=NotificationUpdate,
    status_code=200
)
async def create_notification(
        data: NotificationCreate,
        user: User = Depends(get_logged_user),
):
    """Create notification for user by user database id

    :param created_at: string - Datetime in format: "2022-12-02T10:48:56.528Z"
    or "2022-12-02 10:48:56"

    :param text: string - Description text

    :return: Notification created information as JSON
    """

    data: dict = data.validate_datetime().dict()
    data['user_id'] = user.id
    notification: Notification = await CRUD.notification.create(data)
    logger.info(f"Notification with id {notification.id} created")

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationUpdate
)
async def get_notification(
        notification_id: int,
        user: User = Depends(get_logged_user)
):
    """Get notification by its id. Need authorization.

    :param notification_id: integer - Notification id in database

    :return: Notification data as JSON
    """
    notification = await CRUD.notification.get_by_id(notification_id)
    if notification and notification.user_id == user.id:
        return notification
    raise NotificationNotFound


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_logged_user)]
)
async def delete_notification(
        notification_id: int,
):
    """Delete notification by its id. Need authorization.

    :param notification_id: integer - Notification id in database

    :return: None
    """
    notification: Notification = await CRUD.notification.get_by_id(notification_id)
    if not notification:
        raise NotificationNotFound
    await CRUD.notification.delete(notification)

    logger.info(f"Notification with id {notification_id} deleted")
