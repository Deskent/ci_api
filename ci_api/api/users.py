from fastapi import APIRouter, Depends, HTTPException, status

from config import logger
from models.models import User, Alarm, Notification, Rate
from schemas.alarms import AlarmBase
from schemas.user_schema import UserSchema, UserEditProfile
from services.depends import get_logged_user
from services.rates_cache import RatesCache
from services.weekdays import WeekDay
from web_service.handlers.profile_web_contexts import get_edit_profile_web_context

router = APIRouter(prefix="/users", tags=['Users'])


@router.get("/alarms/list", response_model=list[AlarmBase])
async def get_user_alarms(
        user: User = Depends(get_logged_user),
):
    """Get all user alarms. Need authorization.

    :return List of alarms as JSON
    """

    alarms_data: list = await Alarm.get_all_by_user_id(user.id)
    alarms: list[dict] = [elem.dict() for elem in alarms_data]
    for alarm in alarms:
        alarm['weekdays'] = WeekDay(alarm['weekdays']).as_list

    logger.info(f"User with id {user.id} request alarms")

    return alarms


@router.get("/notifications", response_model=list[Notification])
async def get_user_notifications(
        user: User = Depends(get_logged_user),
):
    """Get all user notifications. Need authorization.

    :return List of notifications
    """

    notifications: list = await Notification.get_all_by_user_id(user.id)
    logger.info(f"User with id {user.id} request notifications")

    return notifications


@router.get("/rates", response_model=list[Rate])
async def get_all_rates():
    """Get all rates.

    :return List of rates
    """

    rates: list[Rate] = await RatesCache.get_all()
    logger.info(f"Rates requested")

    return rates


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[])
async def delete_user(
        logged_user: User = Depends(get_logged_user),
):
    """
    Delete user by user_id. Need authorization.

    :param user_id: int - User database ID

    :return: None
    """

    if not (user := await User.get_by_id(logged_user.id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user.delete()
    logger.info(f"User with id {user.id} deleted")


@router.get("/me", response_model=UserSchema)
async def get_me(
        user: User = Depends(get_logged_user)
):
    """
    Get user info. Need authorization.

    :return: User as JSON
    """

    logger.info(f"User with id {user.id} request @me")

    return user


@router.put(
    "/edit",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
async def edit_user_api(
        user_data: UserEditProfile,
        user: User = Depends(get_logged_user)
):
    """
    Update user in database from optional parameters.
    For user self and admins only.

    :param username: string - Имя

    :param last_name: string - Фамилия

    :param third_name: string - Отчество

    :param email: string - E-mail (Unique)

    :param phone: string - Password (Unique)

    :return: User updated information as JSON
    """

    web_context = await get_edit_profile_web_context(context={}, user_data=user_data, user=user)
    return web_context.api_render()

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
