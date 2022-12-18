from config import logger
from models.models import BaseSQLModel, Rate, Complex, User, Video, Avatar


models_types = BaseSQLModel | Rate | Complex | User | Video | Avatar


class AllCache:
    __data = {}

    @classmethod
    async def initialise(cls, model: models_types) -> None:
        logger.debug(f"Initialization cache for {model}")
        data: list[models_types] = await model.get_all()
        await cls.update_data(model, data)

    @classmethod
    async def update_data(cls, model: models_types, data: list[models_types]) -> None:
        key: str = cls.__get_model_name(model)
        logger.debug(f"data[{key}] updated: {data}")
        cls.__data[key] = {elem.id: elem for elem in data}

    @classmethod
    async def get_by_id(cls, model: models_types, id_: int) -> models_types:
        key: str = cls.__get_model_name(model)
        if not cls.__data.get(key, {}):
            await cls.initialise(model)
        if id_ in cls.__data[key]:
            result: models_types = cls.__data[key][id_]
            if not result:
                result: models_types = await model.get_by_id(id_)

            return result

    @classmethod
    async def get_all(cls, model: models_types) -> list[models_types]:
        key: str = cls.__get_model_name(model)
        if not cls.__data[key]:
            await cls.initialise(model)

        return [elem for elem in cls.__data[key].values()]

    @classmethod
    def __get_model_name(cls, model: models_types) -> str:
        return model.__name__.lower()
