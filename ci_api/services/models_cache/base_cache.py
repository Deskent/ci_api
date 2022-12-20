from config import logger
from models.models import BaseSQLModel, Rate, Complex, User, Video, Avatar


models_types = BaseSQLModel | Rate | Complex | User | Video | Avatar


class AllCache:
    __data = {}

    @classmethod
    async def update_data(cls, model: models_types, data: list[models_types]) -> None:
        key: str = cls.__get_model_name(model)
        logger.debug(f"data[{key}] updated: {data}")
        cls.__data[key] = {elem.id: elem for elem in data}

    @classmethod
    async def get_by_id(cls, model: models_types, id_: int) -> models_types:
        key: str = cls.__get_model_name(model)
        if key in cls.__data.keys():
            return cls.__data[key].get(id_, None)

    @classmethod
    async def get_all(cls, model: models_types) -> list[models_types]:
        key: str = cls.__get_model_name(model)
        if key in cls.__data.keys():
            return [elem for elem in cls.__data[key].values()]
        return []

    @classmethod
    def __get_model_name(cls, model: models_types) -> str:
        return model.__name__.lower()
