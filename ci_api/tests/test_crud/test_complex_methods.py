from models.crud import Complex
from models.crud_back import ComplexCRUD


async def test_complex_create():
    data = {
        "description": "Описание комплекса 99",
        "name": "комплекс 99",
        "number": 99,
        "duration": 99
    }
    complex_data = await ComplexCRUD().create(data)
    assert complex_data is not None


async def test_complex_get_by_id():
    complex_data = await ComplexCRUD().get_by_id(1)
    assert complex_data is not None


async def test_complex_update():
    all_complexes: list[Complex] = await ComplexCRUD().get_all()
    last_id: Complex = max(all_complexes, key=lambda x: x.id)
    complex_data: Complex = await ComplexCRUD().get_by_id(last_id.id)
    assert complex_data.duration == 99
    complex_data.duration = 100
    new_data: Complex = await ComplexCRUD().update(complex_data)
    assert new_data.duration == 100


async def test_get_next_complex():
    complex_data: Complex = await ComplexCRUD().get_by_id(1)
    next_complex_id: int = await ComplexCRUD().next_complex_id(complex_data)
    assert next_complex_id == 2


async def test_complex_delete():
    deleting_complexes: list[Complex] = await ComplexCRUD().get_all()
    last_id: Complex = max(deleting_complexes, key=lambda x: x.id)
    complex_data = await ComplexCRUD().delete_by_id(last_id.id)
    assert complex_data is None
