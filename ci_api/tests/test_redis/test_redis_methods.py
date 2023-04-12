import pytest

from misc.redis_class import RedisDB
from database.models import Rate
from config import db


@pytest.fixture(scope='package')
def redis_client():
    return db.REDIS_DB


async def test_redis_health_check(event_loop, redis_client):

    result = await RedisDB(model=Rate, client=redis_client)._health_check()
    assert result == {'test': 'test'}
    assert await RedisDB(model=Rate, client=redis_client).delete_key() is None


async def test_redis_save_load_rates(all_rates, event_loop, redis_client):
    redis = RedisDB(model=Rate, client=redis_client)
    await redis.save_all(all_rates, 60)
    result: list[Rate] = await redis.load_all()
    assert all_rates[:] == result
    assert await redis.delete_key() is None


async def test_redis_get_by_id(all_rates, event_loop, redis_client):
    rate_id = 1
    redis = RedisDB(model=Rate, client=redis_client)
    await redis.save_all(all_rates, 60)
    result = await redis.get_by_id(rate_id)
    assert result.id == rate_id


async def test_redis_save_by_id(all_rates, event_loop, redis_client):
    redis = RedisDB(model=Rate, client=redis_client)
    await redis.save_all(all_rates, 60)
    new_rate = Rate(**{
                'id': 10000,
                'name': 'New_test_rate',
                'price': -15,
                'duration': 1
            })

    await redis.save_by_id(id_=new_rate.id, data=new_rate)
    result = await redis.get_by_id(new_rate.id)
    assert result.id == new_rate.id
    assert len(await redis.load_all()) > 0
    assert await redis.delete_key() is None
    assert len(await redis.load_all()) == 0
