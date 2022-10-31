from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from database.db import get_session
from models.models import User, UserCreate, UserUpdate, Alarm, Notification, Video

users_router = APIRouter()
TAGS = ['Users']


@users_router.get("/", response_model=list[User], tags=TAGS)
async def get_users(session: AsyncSession = Depends(get_session)):
    """
    Get all users from database

    :return: List of users
    """

    users = await session.execute(select(User))
    return users.scalars().all()


@users_router.get("/<int: user_id>", response_model=User, tags=TAGS)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user by user_id

    :param user_id: ID user in database

    :return: User information
    """

    if not (user := await session.get(User, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@users_router.post("/", response_model=User, tags=TAGS)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Create new user in database if not exists

    :param username: Username

    :param email: E-mail

    :param password: Password

    :return: User created information
    """

    user = User(**data.dict())
    session.add(user)
    await session.commit()

    return user


@users_router.put("/<int: user_id>", response_model=User, tags=TAGS)
async def update_user(user_id: int, data: UserUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update user in database from data

    :param username: Username

    :param email: E-mail

    :param password: Password

    :param expired_at: Date subscribe expiration in format "2022-11-30[T]09:20[:31.777132]"

    :param is_admin: Flag is user admin

    :param is_active: Flag is user have active subscibe

    :param current_video: ID next video in database

    :return: User updated information
    """

    if not (user := await session.get(User, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await user.update_data(session, data, user_id)

    return user


@users_router.delete("/<int: user_id>", status_code=status.HTTP_204_NO_CONTENT, tags=TAGS)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Delete user by user_id

    :param user_id: ID user in database

    :return: None
    """

    if not (user := await session.get(User, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()

    return None


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
#
#
# @users_router.get("/<int: user_id>/get_current_video", response_model=Video, tags=TAGS)
# async def get_user_current_video(user_id: int, session: AsyncSession = Depends(get_session)):
#     """
#
#     :param user_id: User id in database
#     :return: Current user video
#     """
#
#     user: User = await session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     return user.current_video