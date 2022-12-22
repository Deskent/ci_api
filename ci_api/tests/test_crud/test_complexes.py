from database.models import Complex
from crud_class.crud import CRUD


async def test_complex_get_by_id(get_complex):
    complex_data = await CRUD.complex.get_by_id(get_complex.id)
    assert complex_data is not None


async def test_complex_update(get_complex):
    assert get_complex.duration == 99
    get_complex.duration = 100
    new_data: Complex = await CRUD.complex.save(get_complex)
    assert new_data.duration == 100


async def test_get_next_complex(get_complex):
    complex_data: Complex = await CRUD.complex.get_by_id(get_complex.id)
    next_complex: Complex = await CRUD.complex.next_complex(complex_data)
    assert next_complex.id == 1


async def test_crud_get_all_complexes():
    data: list[Complex] = await CRUD.complex.get_all()
    assert data[0].id > 0
