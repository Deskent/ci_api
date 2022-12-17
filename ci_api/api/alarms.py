from fastapi import APIRouter, Depends, status

from config import logger
from models.models import Alarm, User
from schemas.alarms import AlarmCreate, AlarmFull, AlarmUpdate
from services.alarms_web_context import get_update_alarm_web_context, get_alarm_or_raise
from services.depends import get_logged_user
from services.web_context_class import WebContext
from services.weekdays import WeekDay

router = APIRouter(prefix="/alarms", tags=['Alarms'])


@router.post(
    "/",
    response_model=AlarmFull,
    status_code=status.HTTP_200_OK
)
async def create_alarm(
        data: AlarmCreate,
        user: User = Depends(get_logged_user),
):
    """Create alarm for user by user database id. Need authorization.

    :param alarm_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param weekdays: list[string] - List of week days in format
        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        or
        ['all']
        default='all'

    :param sound_name: string - Name of sound for current alarm

    :param volume: int - Volume level 0 to 100 , default=50

    :param vibration: bool - Vibration switcher, default=False

    :param text: string - Description text

    :return: Alarm created information as JSON
    """

    payload: dict = data.dict()
    payload.update({"user_id": user.id})
    week_days: WeekDay = WeekDay(data.weekdays)
    payload.update(weekdays=week_days.as_string)
    alarm: Alarm = Alarm(**payload)
    await alarm.save()
    alarm.weekdays = week_days.as_list
    logger.info(f"Alarm with id {alarm.id} created")

    return alarm


@router.put(
    "/{alarm_id}",
    response_model=AlarmFull,
    status_code=status.HTTP_200_OK
)
async def update_alarm(
        alarm_id: int,
        data: AlarmUpdate,
        user: User = Depends(get_logged_user)
):
    """Update alarm by its id and data. Need authorization.

    :param alarm_id: integer - Alarm id in database

    :return: Alarm as JSON
    """

    alarm: Alarm = await get_alarm_or_raise(alarm_id, user)
    web_context: WebContext = await get_update_alarm_web_context({}, alarm, data)
    return web_context.api_render()


@router.delete(
    "/{alarm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_alarm(
        alarm_id: int,
        user: User = Depends(get_logged_user)
):
    """Delete alarm by its id. Need authorization.

    :param alarm_id: integer - Alarm id in database

    :return: None
    """

    alarm: Alarm = await get_alarm_or_raise(alarm_id, user)
    await alarm.delete()
    logger.info(f"Alarm with id {alarm_id} deleted")


@router.get(
    "/{alarm_id}",
    response_model=AlarmFull,
    status_code=status.HTTP_200_OK
)
async def get_alarm_by_id(
        alarm_id: int,
        user: User = Depends(get_logged_user),
):
    """Return alarm by its id. Need authorization.

    :param alarm_id: integer - Alarm id in database

    :return: Alarm as JSON
    """

    alarm: Alarm = await get_alarm_or_raise(alarm_id, user)
    alarm.weekdays = WeekDay(alarm.weekdays).as_list
    return alarm
