from fastapi import status, HTTPException

from models.models import Alarm, User
from schemas.alarms import AlarmUpdate
from services.web_context_class import WebContext
from services.weekdays import WeekDay


async def get_alarm_or_raise(alarm_id: int, user: User):
    alarm: Alarm = await user.get_alarm_by_id(alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
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

    await alarm.save()
    alarm.weekdays = WeekDay(alarm.weekdays).as_list
    alarm.alarm_time = alarm.alarm_time.strftime("%H:%M")
    web_context.api_data.update(payload=alarm)

    return web_context
