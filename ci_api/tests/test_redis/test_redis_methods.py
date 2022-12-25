import pytest

from config import REDIS_CLIENT
from crud_class.crud import CRUD
from misc.redis_class import RedisDB
from database.models import User, Rate


@pytest.fixture
def redis():
    return RedisDB(client=REDIS_CLIENT, model=User)


@pytest.mark.server
async def test_redis_health_check(redis):

    result = await redis._health_check()
    assert result == {'test': 'test'}
    assert await redis.delete_key() is None


@pytest.mark.server
async def test_redis_save_load_rates():
    redis = RedisDB(model=Rate, client=REDIS_CLIENT)
    rates: list[Rate] = await CRUD.rate.get_all()
    await redis.save_all(rates, 60)
    result: list[Rate] = await redis.load_all()
    assert rates == result
    assert await redis.delete_key() is None


@pytest.mark.server
async def test_redis_get_by_id():
    rate_id = 1
    redis = RedisDB(model=Rate, client=REDIS_CLIENT)
    rates: list[dict] = await CRUD.rate.get_all()
    await redis.save_all(rates, 60)
    result = await redis.get_by_id(rate_id)
    assert result.id == rate_id


@pytest.mark.server
async def test_redis_save_by_id():
    redis = RedisDB(model=Rate, client=REDIS_CLIENT)
    rates: list[dict] = await CRUD.rate.get_all()
    await redis.save_all(rates, 60)
    new_rate = Rate(**{
                'id': 3,
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

