from fastapi import APIRouter, Depends, status, HTTPException

from config import logger
from models.models import Alarm, User
from schemas.alarms import AlarmCreate, AlarmFull
from services.depends import get_logged_user
from services.weekdays import WeekDay

router = APIRouter(prefix="/alarms", tags=['Alarms'])


@router.post(
    "/",
    response_model=AlarmFull
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


@router.get(
    "/{alarm_id}",
    response_model=AlarmFull,
    status_code=200
)
async def get_alarm(
        alarm_id: int,
        user: User = Depends(get_logged_user),
):
    alarm: Alarm = await Alarm.get_by_id(alarm_id)
    if alarm and alarm.user_id == user.id:
        alarm.weekdays = WeekDay(alarm.weekdays).as_list
        return alarm
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")


@router.delete(
    "/{alarm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_logged_user)]
)
async def delete_alarm(
        alarm_id: int,
):
    """Delete alarm by its id. Need authorization.

    :param alarm_id: integer - Alarm id in database

    :return: None
    """

    alarm: Alarm = await Alarm.get_by_id(alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    await alarm.delete()
    logger.info(f"Alarm with id {alarm_id} deleted")
