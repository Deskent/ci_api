from models.models import Rate


class RatesCache:
    rates = {}

    @classmethod
    async def update_rates(cls, rates: list[Rate]) -> None:
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
        return [rate for rate in cls.rates.values()]
