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

    def without_seconds(self):
        self.alarm_time = self.alarm_time.strftime('%H:%M')
        return self

class AlarmUpdate(BaseModel):
    alarm_time: time = None
    weekdays: list[str] = None
    sound_name: str = None
    volume: int = None
    vibration: bool = False
    text: str = None
