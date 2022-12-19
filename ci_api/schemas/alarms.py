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


class AlarmFull(AlarmBase):
    id: int
    alarm_time: str


class AlarmUpdate(BaseModel):
    alarm_time: time = None
    weekdays: list[str] = None
    sound_name: str = None
    volume: int = None
    vibration: bool = False
    text: str = None
