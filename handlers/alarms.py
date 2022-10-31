from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import Alarm, AlarmCreate, AlarmUpdate


alarms_router = APIRouter()
TAGS = ['Alarms']


@alarms_router.post("/", response_model=Alarm, tags=TAGS)
async def create_alarm(data: AlarmCreate, session: AsyncSession = Depends(get_session)):
    """Create alarm for user by user database id

    :param alarm_time: String, in HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]] format

    :param text: String, some text

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

    :param data: Data which will be updated

    :return: Alarm updated information.
    """

    alarm: Alarm = await session.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")

    return await alarm.update_data(session, data)


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