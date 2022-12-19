import pytest

from models.models import Rate, Complex
from services.models_cache.crud import CRUD


@pytest.mark.skip
async def test_cache_rates():
    rates: list[Rate] = await CRUD.rate.get_all()
    assert rates is not None
    assert rates[0].name == 'Free'


@pytest.mark.skip
async def test_cache_complexes():
    data: list[Complex] = await CRUD.complex.get_all()
    assert data is not None
    assert data[0].id > 0
