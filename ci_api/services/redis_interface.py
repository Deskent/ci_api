import pickle
from abc import abstractmethod

import aioredis

from models.models import User, Complex, Avatar, Rate
from config import logger, REDIS_CLIENT

MODEL_TYPES = User | Complex | Avatar | Rate


class RedisException(Exception):
    pass


class RedisBase:

    def __init__(
            self,
            key: str = None,
            model: MODEL_TYPES = None,
            id_: int = None,
            client: aioredis.Redis = REDIS_CLIENT
    ):
        super().__init__()
        if id_:
            self.id_ = id_
        elif model:
            self.id_ = model.id
        else:
            self.id_ = None
        self.key: str = ''
        if key:
            self.key: str = key
        elif model:
            self.key: str = model.__name__.lower()
        self.redis = client
        self.model = model


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

    def __init__(self, data: list | dict, timeout_sec: int = 60, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_sec: int = timeout_sec
        self._data: list | dict = data

    async def execute(self) -> None:
        value: bytes = pickle.dumps(self._data)
        return await self.redis.set(name=self.key, value=value, ex=self.timeout_sec)


class GetRedisDB(RedisOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def execute(self) -> dict:
        data: bytes = await self.redis.get(self.key)
        return {"data": pickle.loads(bytes(data))}


class DeleteRedisDB(RedisOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def execute(self) -> None:
        await self.redis.delete(self.key)


class RedisDB(RedisBase):
    """

    {
        "user_id" : {
            "user": data...
            "alarms": data...
        }

    }

    {
        "rates": [Rate]
    }

    {
        "complex_id : {
            "complex": { Complex data
            }
            "videos": [Video]
        }
    }

    """

    def __init__(
            self,
            key: str = None,
            model: MODEL_TYPES = None,
            id_: int = None,
            client: aioredis.Redis = REDIS_CLIENT
    ):
        super().__init__(key=key, model=model, id_=id_, client=client)

    def __check_key(self):
        # TODO сделать декоратором
        if not self.key:
            raise ValueError('Key or model required')

    async def save(self, data: list | dict, timeout_sec: int = 1) -> None:
        self.__check_key()
        return await SetRedisDB(
            key=self.key, model=self.model, data=data, timeout_sec=timeout_sec).run()

    async def load(self) -> dict[str, list | dict]:
        self.__check_key()
        return await GetRedisDB(key=self.key, model=self.model).run()

    async def delete_key(self) -> None:
        self.__check_key()
        return await DeleteRedisDB(key=self.key, model=self.model).run()

    async def health_check(self):
        """Проверяет работу Редис"""
        self.__check_key()
        logger.info("Redis checking...")
        test_data = ['test']
        await self.save(test_data, 60)
        return await self.load()
