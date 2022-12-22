import pytest

from config import REDIS_CLIENT
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
