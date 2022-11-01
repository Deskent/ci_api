from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Alarm, AlarmCreate, AlarmUpdate
from services.utils import get_data_for_update

alarms_router = APIRouter()
TAGS = ['Alarms']


@alarms_router.post("/", response_model=Alarm, tags=TAGS)
async def create_alarm(data: AlarmCreate, session: AsyncSession = Depends(get_session)):
    """Create alarm for user by user database id

    :param alarm_time: string, in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: String, Description text

    :param user_id: Integer, user id in database

    :return: Alarm created information.
    """

    alarm: Alarm = Alarm(**data.dict())
    session.add(alarm)
    await session.commit()

    return alarm


@alarms_router.put("/<int: alarm_id>", response_model=Alarm, tags=TAGS)
async def update_alarm(alarm_id: int, data: AlarmUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update alarm by id

    :param alarm_id: Alarm id in database

    :param alarm_time: string, in format HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]

    :param text: string - Description text

    :return: Alarm updated information.
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    updated_data: dict = await get_data_for_update(data.dict())
    await session.execute(update(Alarm).where(Alarm.id == alarm_id).values(**updated_data))
    session.add(alarm)
    await session.commit()

    return alarm


@alarms_router.delete("/<int: alarm_id>", status_code=status.HTTP_204_NO_CONTENT, tags=TAGS)
async def delete_alarm(alarm_id: int, session: AsyncSession = Depends(get_session)):
    """Delete alarm by its id

    :param alarm_id: Alarm id in database

    :return: None
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    await session.delete(alarm)
    await session.commit()
