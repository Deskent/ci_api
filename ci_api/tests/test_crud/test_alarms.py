import pytest

from database.models import Alarm
from crud_class.crud import CRUD


async def test_get_all_active_alarms():
    alarms: list[Alarm] = await CRUD.alarm.get_all_active_alarms()
    assert alarms is not None
