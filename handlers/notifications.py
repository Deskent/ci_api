from fastapi import APIRouter, Request, Depends, status, HTTPException
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db import get_session
from app.models import Notification, NotificationCreate, NotificationUpdate, User


notifications_router = APIRouter()
TAGS = ['Notifications']


@notifications_router.post("/", response_model=Notification, tags=TAGS)
async def create_notification(data: NotificationCreate, session: AsyncSession = Depends(get_session)):
    notification: Notification = Notification(**data.dict())
    session.add(notification)
    await session.commit()

    return notification


@notifications_router.put("/<int: notification_id>", response_model=Notification, tags=TAGS)
async def update_notification(notification_id: int, data: NotificationUpdate, session: AsyncSession = Depends(get_session)):
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    return await notification.update_data(session, data)


@notifications_router.delete("/<int: notification_id>", status_code=status.HTTP_204_NO_CONTENT, tags=TAGS)
async def delete_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    notification: Notification = await session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await session.delete(notification)
    await session.commit()
