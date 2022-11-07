from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Notification, NotificationCreate, NotificationUpdate
from services.utils import get_data_for_update

router = APIRouter(prefix="/notifications", tags=['Notifications'])


@router.post("/", response_model=Notification)
async def create_notification(data: NotificationCreate, session: AsyncSession = Depends(get_session)):
    """Create notification for user by user database id

    :param notification_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :param user_id: integer - user id in database

    :return: Notification created information as JSON
    """

    notification: Notification = Notification(**data.dict())
    session.add(notification)
    await session.commit()

    return notification


@router.put("/{notification_id}", response_model=Notification)
async def update_notification(notification_id: int, data: NotificationUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update notification by id

    :param notification_id: integer Notification id in database

    :param notification_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :return: Notification updated information as JSON
    """

    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    updated_data: dict = await get_data_for_update(data.dict())
    await session.execute(update(Notification).where(Notification.id == notification_id).values(**updated_data))
    session.add(notification)
    await session.commit()

    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    """Delete notification by its id

    :param notification_id: integer - Notification id in database

    :return: None
    """
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await session.delete(notification)
    await session.commit()
