import pickle
from abc import abstractmethod

import aioredis

from config import logger, get_redis_client
from crud_class.ci_types import MODEL_TYPES

HOURS = 1
STORE_TIME_SEC = 60 * 60 * HOURS


class RedisException(Exception):
    pass


class RedisBase:
    """

    Store data in redis.

    Attributes

        model: [Database model] - Using for create key for save data

        id_: int - Using for create key for save instance data

    """

    def __init__(
            self,
            model: MODEL_TYPES,
            client: aioredis.Redis = None
    ):
        self.redis: aioredis.Redis = client or next(get_redis_client())
        self.model: MODEL_TYPES = model
        self.id_: int = 0
        self.key: str = self.model.__name__.lower() + 's'


class RedisOperator(RedisBase):

    async def run(self):
        try:
            return await self.execute()
        except ConnectionRefusedError as err:
            error_text = (f"Unable to connect to redis, data: not saved!"
                          f"\n {err}")
        except aioredis.exceptions.ConnectionError as err:
            error_text = f"Connection error: {err}"
        # except Exception as err:
        #     error_text = f"Exception Error: {err}"

        raise RedisException(error_text)

    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError


class SetRedisDB(RedisOperator):

    def __init__(self, data: dict[str, MODEL_TYPES], timeout_sec: int = STORE_TIME_SEC, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_sec: int = timeout_sec
        self._data: dict[str, MODEL_TYPES] = data

    async def execute(self) -> None:
        value: bytes = pickle.dumps(self._data)
        return await self.redis.set(name=self.key, value=value, ex=self.timeout_sec)


class GetRedisDB(RedisOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def execute(self) -> dict[str, MODEL_TYPES]:
        data: bytes = await self.redis.get(self.key)
        if not data:
            return {}
        return pickle.loads(bytes(data))


class DeleteRedisDB(RedisOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def execute(self) -> None:
        await self.redis.delete(self.key)


class RedisDB(RedisBase):
    """
    Save as structure
    {
       "rate": {
                    "1": {
                            Rate("id": 1, "name" ...)
                    },
                    "2": {
                            Rate("id": 2, "name" ...)
                    },
                    ...
       },
       "user": {
                    ...
       }

    }

    """

    def __init__(
            self,
            model: MODEL_TYPES,
            client: aioredis.Redis = get_redis_client()
    ):
        super().__init__(model=model, client=client)

    async def _save(self, data: dict[str, MODEL_TYPES], timeout_sec: int = STORE_TIME_SEC) -> None:
        return await SetRedisDB(model=self.model, data=data, timeout_sec=timeout_sec).run()

    async def _load(self) -> dict | list:
        return await GetRedisDB(model=self.model).run()

    async def delete_key(self) -> None:
        return await DeleteRedisDB(model=self.model).run()

    async def _health_check(self):
        """Check redis work"""

        logger.info("Redis checking...")
        test_data = {'test': 'test'}
        await self._save(test_data, 60)
        return await self._load()

    async def save_all(self, data: list[MODEL_TYPES], timeout_sec: int = STORE_TIME_SEC):
        """Overwrite all values for model"""

        logger.debug(f"All {self.model} data saved")

        to_save: dict[str, MODEL_TYPES] = {
            str(elem.id): elem
            for elem in data
        }
        return await self._save(to_save, timeout_sec)

    async def load_all(self) -> list[MODEL_TYPES]:
        """Return all values for model"""

        logger.debug(f"All {self.model} data loaded")

        all_data: dict[str, MODEL_TYPES] = await self._load()
        return list(all_data.values())

    async def get_by_id(self, id_: int) -> MODEL_TYPES:
        """Return element by id if exists"""

        all_elems: dict[str, MODEL_TYPES] = await self._load()

        result = all_elems.get(str(id_), None)
        logger.debug(f"Data {result} loaded")
        return result

    async def save_by_id(self, id_: int, data: MODEL_TYPES) -> None:
        """Overwrite element by id"""

        logger.debug(f"Data {data} saved")
        all_elems: dict[str, MODEL_TYPES] = await self._load()
        all_elems[str(id_)] = data
        await self._save(all_elems)
