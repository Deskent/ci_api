from fastapi import APIRouter, Request, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Notification, NotificationCreate, NotificationUpdate, User
from services.utils import get_data_for_update

notifications_router = APIRouter()
TAGS = ['Notifications']


@notifications_router.post("/", response_model=Notification, tags=TAGS)
async def create_notification(data: NotificationCreate, session: AsyncSession = Depends(get_session)):
    notification: Notification = Notification(**data.dict())
    session.add(notification)
    await session.commit()

    return notification


@notifications_router.put("/{notification_id}", response_model=Notification, tags=TAGS)
async def update_notification(notification_id: int, data: NotificationUpdate, session: AsyncSession = Depends(get_session)):
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    updated_data: dict = await get_data_for_update(data.dict())
    await session.execute(update(Notification).where(Notification.id == notification_id).values(**updated_data))
    session.add(notification)
    await session.commit()

    return notification


@notifications_router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, tags=TAGS)
async def delete_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await session.delete(notification)
    await session.commit()
