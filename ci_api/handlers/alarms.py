from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Alarm, User
from schemas.alarms import AlarmCreate, AlarmFull, AlarmBase
from services.depends import get_logged_user
from services.utils import get_data_for_update
from services.weekdays import WeekDay
from config import logger

router = APIRouter(prefix="/alarms", tags=['Alarms'])


@router.post("/", response_model=AlarmFull)
async def create_alarm(
    data: AlarmCreate,
    user: User = Depends(get_logged_user),
    session: AsyncSession = Depends(get_session)
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
    session.add(alarm)
    await session.commit()
    alarm.weekdays = week_days.as_list
    logger.info(f"Alarm with id {alarm.id} created")

    return alarm


@router.get(
    "/{alarm_id}"
)
async def get_alarm(
        alarm_id: int,
        session: AsyncSession = Depends(get_session),
        user: User = Depends(get_logged_user)
):
    # TODO сделать проверку на то, что аларм для этого пользователя

    if result := await session.get(Alarm, alarm_id):
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")


# TODO сделать
# @router.put("/{alarm_id}", response_model=Alarm)
# async def update_alarm(alarm_id: int, data: AlarmUpdate, session: AsyncSession = Depends(get_session)):
#     """
#     Update alarm by id
#
#     :param alarm_id: integer Alarm id in database
#
#     :param alarm_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]
#
#     :param text: string - Description text
#
#     :return: Alarm updated information as JSON
#     """
#
#     alarm: Alarm = await session.get(Alarm, alarm_id)
#     if not alarm:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
#     updated_data: dict = await get_data_for_update(data.dict())
#     await session.execute(update(Alarm).where(Alarm.id == alarm_id).values(**updated_data))
#     session.add(alarm)
#     await session.commit()
#
#     return alarm


@router.delete(
    "/{alarm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_logged_user)]
)
async def delete_alarm(
        alarm_id: int,
        session: AsyncSession = Depends(get_session)
):
    """Delete alarm by its id. Need authorization.

    :param alarm_id: integer - Alarm id in database

    :return: None
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    await session.delete(alarm)
    await session.commit()
    logger.info(f"Alarm with id {alarm_id} deleted")
