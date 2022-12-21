from crud_class.crud import CRUD
from models.models import Rate


async def test_crud_get_all_rates():
    data: list[Rate] = await CRUD.rate.get_all()
    assert data[0].name == 'Free'


async def test_get_free_rate():
    rate: Rate = await CRUD.rate.get_free()
    assert rate.id > 0
