from models.models import Rate
from config import logger

class RatesCache:
    rates = {}

    @classmethod
    async def update_rates(cls, rates: list[Rate]) -> None:
        logger.debug(f"Rates updated: {rates}")
        cls.rates = {rate.id: rate for rate in rates}

    @classmethod
    async def get_by_id(cls, rate_id: int) -> Rate:
        if rate_id in cls.rates:
            return cls.rates[rate_id]

    @classmethod
    async def initialise(cls) -> None:
        rates: list[Rate] = await Rate.get_all()
        await cls.update_rates(rates)

    @classmethod
    async def get_all(cls) -> list[Rate]:
        result: list[Rate] = [rate for rate in cls.rates.values()]
        if not result:
            all_rates: list[Rate] = await Rate.get_all()
            await cls.update_rates(all_rates)
            result: list[Rate] = [rate for rate in cls.rates.values()]

        return result

