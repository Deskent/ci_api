from exc.exceptions import AlarmNotFound
from models.models import Alarm, User
from schemas.alarms import AlarmUpdate
from crud_class.crud import CRUD
from services.web_context_class import WebContext
from services.weekdays import WeekDay


async def get_alarm_or_raise(alarm_id: int, user: User):
    alarm: Alarm = await CRUD.user.get_alarm_by_alarm_id(user, alarm_id)
    if not alarm:
        raise AlarmNotFound
    return alarm


async def get_update_alarm_web_context(
        context: dict,
        alarm: Alarm,
        data: AlarmUpdate
) -> WebContext:
    """Update alarm from data"""

    if data.weekdays:
        data.weekdays = WeekDay(data.weekdays).as_string

    web_context = WebContext(context)
    for key, value in data.dict().items():
        if value and hasattr(alarm, key):
            if getattr(alarm, key) != value:
                setattr(alarm, key, value)

    alarm: Alarm = await CRUD.alarm.save(alarm)
    alarm: Alarm = await CRUD.alarm.for_response(alarm)
    web_context.api_data.update(payload=alarm)

    return web_context
