import pytest

from config import REDIS_CLIENT
from models.models import Rate
from misc.redis_class import RedisDB


@pytest.fixture
def redis():
    return RedisDB(client=REDIS_CLIENT)


@pytest.mark.server
async def test_redis_health_check(redis):
    redis.key = 'test'
    result = await redis.health_check()
    assert result['data'] == ['test']
    assert await redis.delete_key() is None

@pytest.mark.server
async def test_redis_value_error(redis):
    with pytest.raises(ValueError):
        await redis.health_check()


@pytest.mark.skip
async def test_redis_save_rates():
    rates = await Rate.get_all()
    redis = RedisDB(client=REDIS_CLIENT, model=Rate)
    await redis.save(data=rates)
    data: dict[str, list | dict] = await redis.load()
    assert data['data'] == rates
    assert data['data'][0].id == rates[0].id
