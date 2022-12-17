import pytest

from models.models import Rate, Complex
from services.models_cache.base_cache import AllCache


@pytest.mark.skip
async def test_cache_rates():
    await AllCache.initialise(Rate)
    rates: list[Rate] = await AllCache.get_all(Rate)
    assert rates is not None
    assert rates[0].name == 'Free'


@pytest.mark.skip
async def test_cache_complexes():
    await AllCache.initialise(Complex)
    rates: list[Complex] = await AllCache.get_all(Complex)
    assert rates is not None
    assert rates[0].id > 0
