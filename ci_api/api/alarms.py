from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from config import logger
from exc.exceptions import AlarmNotFound
from database.models import Alarm, User
from schemas.alarms import AlarmCreate, AlarmFull, AlarmUpdate
from services.alarms_web_context import update_alarm_web_context, get_alarm_or_raise
from services.depends import get_logged_user
from crud_class.crud import CRUD
from misc.web_context_class import WebContext

router = APIRouter(prefix="/alarms", tags=['Alarms'])


class AlarmNotFoundErrorDetails(BaseModel):
    detail: str = AlarmNotFound.detail


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
    alarm: Alarm = await CRUD.alarm.create(payload)
    alarm: Alarm = await CRUD.alarm.for_response(alarm)
    logger.info(f"Alarm with id {alarm.id} created")

    return alarm


@router.put(
    "/{alarm_id}",
    response_model=AlarmFull,
    status_code=status.HTTP_200_OK,
    responses={AlarmNotFound.status_code: {
        "model": AlarmNotFoundErrorDetails,
    }}
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
    web_context: WebContext = await update_alarm_web_context({}, alarm, data)
    return web_context.api_render()


@router.delete(
    "/{alarm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={AlarmNotFound.status_code: {
        "model": AlarmNotFoundErrorDetails,
    }}
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
    await CRUD.alarm.delete(alarm)
    logger.info(f"Alarm with id {alarm_id} deleted")


@router.get(
    "/{alarm_id}",
    response_model=AlarmFull,
    status_code=status.HTTP_200_OK,
    responses={AlarmNotFound.status_code: {
        "model": AlarmNotFoundErrorDetails,
    }}
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
    return await CRUD.alarm.for_response(alarm)
