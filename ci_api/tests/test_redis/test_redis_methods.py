import pytest

from config import REDIS_CLIENT
from services.models_cache.redis_interface import RedisDB


@pytest.mark.server
async def test_redis_health_check():
    result = await RedisDB(key='test', client=REDIS_CLIENT).health_check()
    assert result['data'] == ['test']
    assert await RedisDB(key='test').delete_key() is None

@pytest.mark.server
async def test_redis_value_error():
    with pytest.raises(ValueError):
        await RedisDB(client=REDIS_CLIENT).health_check()
