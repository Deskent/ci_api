import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db import get_session
from app.models import *

users_router = APIRouter()
TAGS = ['Users']


@users_router.get("/", response_model=list[UserBase], tags=TAGS)
async def get_users(session: AsyncSession = Depends(get_session)):
    """
    Get all users from database

    :return: List of users
    """
    result = await session.execute(select(User))
    return result.scalars().all()


@users_router.post("/", response_model=User, tags=TAGS)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Create new user in database if not exists
    "username": "string" - Username

    "email": "string" - E-mail

    "password": "string", - Password

    :return: User created information
    """

    expired_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    user = User(**data.dict(), expired_at=expired_at)
    session.add(user)
    await session.commit()

    return user


@users_router.put("/<int: user_id>", response_model=User, tags=TAGS)
async def update_notification(user_id: int, data: UserUpdate, session: AsyncSession = Depends(get_session)):
    user: User = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return await user.update_data(session, data)


@users_router.get("/<int: user_id>/alarms", response_model=list[Alarm], tags=TAGS)
async def get_user_alarms(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get all user alarms"""

    alarms: Row = await session.execute(select(Alarm).join(User).where(User.id == user_id))

    return alarms.scalars().all()


@users_router.get("/<int: user_id>/notifications", response_model=list[Notification], tags=TAGS)
async def get_user_notifications(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get all user notifications"""

    notifications: Row = await session.execute(select(Notification).join(User).where(User.id == user_id))

    return notifications.scalars().all()
