from datetime import time

from pydantic import BaseModel


class AlarmBase(BaseModel):
    alarm_time: time
    week_days: str
    sound_name: str
    volume: int
    vibration: bool
    text: str = None


class AlarmCreate(AlarmBase):
    user_id: int


class AlarmUpdate(AlarmCreate):
    pass
