from datetime import time

from pydantic import BaseModel


class AlarmBase(BaseModel):
    alarm_time: time
    weekdays: list[str]
    sound_name: str
    volume: int
    vibration: bool
    text: str = None


class AlarmCreate(AlarmBase):
    pass


class AlarmUpdate(AlarmCreate):
    pass
