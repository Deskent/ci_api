from fastapi import APIRouter, Depends, status

from config import logger
from exc.exceptions import UserNotFoundErrorApi
from database.models import User, Alarm, Notification, Rate
from schemas.alarms import AlarmFull
from schemas.user_schema import UserSchema, UserEditProfile, EntryModalWindow, UserMood
from services.depends import get_logged_user
from crud_class.crud import CRUD
from misc.weekdays_class import WeekDay
from services.user import get_modal_window_first_entry
from web_service.handlers.profile_web_contexts import get_edit_profile_web_context

router = APIRouter(prefix="/users", tags=['Users'])


@router.get(
    "/alarms/list",
    response_model=list[AlarmFull],
    status_code=status.HTTP_200_OK,
    tags=['Alarms']
)
async def get_user_alarms(
        user: User = Depends(get_logged_user),
):
    """Get all user alarms. Need authorization.

    :return List of alarms as JSON
    """
    alarms_data: list[Alarm] = await CRUD.alarm.get_all_by_user_id(user.id)
    alarms: list[dict] = [elem.dict() for elem in alarms_data]
    for alarm in alarms:
        alarm['weekdays'] = WeekDay(alarm['weekdays']).as_list
        alarm['alarm_time'] = alarm['alarm_time'].strftime("%H:%M")

    logger.info(f"User with id {user.id} request alarms")

    return alarms


@router.get(
    "/notifications",
    response_model=list[Notification],
    status_code=status.HTTP_200_OK,
    tags=["Notifications"]
)
async def get_user_notifications(
        user: User = Depends(get_logged_user),
):
    """Get all user notifications. Need authorization.

    :return List of notifications
    """

    notifications: list[Notification] = await CRUD.notification.get_all_by_user_id(user.id)
    logger.info(f"User with id {user.id} request notifications")

    return notifications


@router.get(
    "/rates",
    response_model=list[Rate],
    dependencies=[Depends(get_logged_user)],
    status_code=status.HTTP_200_OK,
    tags=['Rates']
)
async def get_all_rates():
    """Get all rates.

    :return List of rates
    """

    rates: list[Rate] = await CRUD.rate.get_all()
    logger.info(f"Rates requested")

    return rates


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
        logged_user: User = Depends(get_logged_user),
):
    """
    Delete user by user_id. Need authorization.

    :param user_id: int - User database ID

    :return: None
    """

    if not (user := await CRUD.user.get_by_id(logged_user.id)):
        raise UserNotFoundErrorApi
    await CRUD.user.delete(user)
    logger.info(f"User with id {user.id} deleted")


@router.get(
    "/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
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


@router.get(
    "/check_first_entry",
    status_code=status.HTTP_200_OK,
    response_model=EntryModalWindow
)
async def check_first_entry_or_new_user(
        user: User = Depends(get_logged_user)
):
    """
    Return today_first_entry = True and list of emojies if user
    entered first time today and user level > 6.

    Return new_user = True if user registered now have first entry and
    object 'hello_video' with hello video data.

    Return is_expired = True if user subscribe expired.

    Return user as JSON else.

    :param user: Logged user

    :return: JSON
    """

    return await get_modal_window_first_entry(user)


@router.post(
    "/set_user_mood",
    status_code=status.HTTP_202_ACCEPTED
)
async def set_user_mood(
        mood: UserMood,
        user: User = Depends(get_logged_user)
):
    """
    Set mood for user

    :return: null
    """
    await CRUD.user.set_mood(mood.mood_id, user=user)
