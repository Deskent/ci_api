from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Alarm, User
from schemas.alarms import AlarmCreate, AlarmUpdate, AlarmBase
from services.depends import get_logged_user
from services.utils import get_data_for_update
from services.weekdays import WeekDay

router = APIRouter(prefix="/alarms", tags=['Alarms'])


@router.post("/", response_model=AlarmBase)
async def create_alarm(
    data: AlarmCreate,
    user: User = Depends(get_logged_user),
    session: AsyncSession = Depends(get_session)
):
    """Create alarm for user by user database id

    :param alarm_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param weekdays: list[string] - List of week days in format
        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        or
        ['all']

    :param text: string - Description text

    :return: Alarm created information as JSON
    """

    payload: dict = data.dict()
    payload.update({"user_id": user.id})
    week_days_string: str = WeekDay.to_string(data.weekdays)
    payload.update(weekdays=week_days_string)
    alarm: Alarm = Alarm(**payload)
    session.add(alarm)
    await session.commit()
    alarm.weekdays = WeekDay.to_list(week_days_string)

    return alarm


@router.put("/{alarm_id}", response_model=Alarm)
async def update_alarm(alarm_id: int, data: AlarmUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update alarm by id

    :param alarm_id: integer Alarm id in database

    :param alarm_time: string - Time in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :return: Alarm updated information as JSON
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    updated_data: dict = await get_data_for_update(data.dict())
    await session.execute(update(Alarm).where(Alarm.id == alarm_id).values(**updated_data))
    session.add(alarm)
    await session.commit()

    return alarm


@router.delete("/{alarm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alarm(alarm_id: int, session: AsyncSession = Depends(get_session)):
    """Delete alarm by its id

    :param alarm_id: integer - Alarm id in database

    :return: None
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    await session.delete(alarm)
    await session.commit()
