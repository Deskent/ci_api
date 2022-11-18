from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import logger
from database.db import get_session
from models.models import User, Alarm, Notification
from schemas.alarms import AlarmBase
from services.depends import get_logged_user
from services.weekdays import WeekDay

router = APIRouter(prefix="/users", tags=['Users'])


@router.get("/alarms", response_model=list[AlarmBase])
async def get_user_alarms(
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """Get all user alarms. Need authorization.

    :return List of alarms as JSON
    """

    query = select(Alarm).join(User).where(User.id == user.id)
    response = await session.execute(query)

    alarms = response.scalars().all()
    results: list[dict] = [elem.dict() for elem in alarms]
    for alarm in results:
        alarm['weekdays'] = WeekDay(alarm['weekdays']).as_list

    logger.info(f"User with id {user.id} request alarms")

    return results


@router.get("/notifications", response_model=list[Notification])
async def get_user_notifications(
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """Get all user notifications. Need authorization.

    :return List of notifications
    """

    query = select(Notification).join(User).where(User.id == user.id)
    notifications = await session.execute(query)
    logger.info(f"User with id {user.id} request notifications")

    return notifications.scalars().all()


@router.get("/me", response_model=User)
async def get_me(
        user: User = Depends(get_logged_user)
):
    """
    Get user info. Need authorization.

    :return: User as JSON
    """

    logger.info(f"User with id {user.id} request @me")

    return user


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Delete user by user_id. Need authorization.

    :param user_id: int - User database ID

    :return: None
    """

    if not (user := await session.get(User, user.id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()
    logger.info(f"User with id {user.id} deleted")

    return None


# @router.put(
#     path="/{user_id}",
#     response_model=UserOutput,
#     dependencies=[Depends(check_access), Depends(check_user_is_admin)]
# )
# async def update_user(
#         user_id: int,
#         data: UserUpdate,
#         session: AsyncSession = Depends(get_session),
# ):
#     """
#     Update user in database from optional parameters.
#     For user self and admins only.
#
#     :param username: string - Username
#
#     :param email: string - E-mail (Unique)
#
#     :param password: string - Password
#
#     :param expired_at: string - Date subscribe expiration in format "2022-11-30[T]09:20[:31.777132]"
#
#     :param is_admin: bool - Flag is user admin
#
#     :param is_active: bool - Flag is user have active subscibe
#
#     :param current_video: int - ID next video in database
#
#     :return: User updated information as JSON
#     """
#
#     if not (user := await session.get(User, user_id)):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     updated_data: dict = await get_data_for_update(data.dict())
#
#     if updated_data.get('expired_at'):
#         updated_data['expired_at'] = updated_data['expired_at'].replace(tzinfo=None)
#
#     password: str = updated_data.get('password')
#     if password:
#         updated_data['password'] = auth_handler.get_password_hash(password)
#
#     email: EmailStr = updated_data.get('email')
#     if email:
#         if await User.get_user_by_email(session, email):
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
#
#     if updated_data.get('current_video') == 0:
#         updated_data['current_video'] = user.current_video
#
#     await session.execute(update(User).where(User.id == user_id).values(**updated_data))
#     session.add(user)
#     await session.commit()
#
#     return user
