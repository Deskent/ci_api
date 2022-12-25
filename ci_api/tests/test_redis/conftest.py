import pytest

from crud_class.crud import CRUD
from database.models import Rate


@pytest.fixture
async def all_rates() -> list[Rate]:
    rates: list[Rate] = await CRUD.rate.get_all()
    yield rates[:]

