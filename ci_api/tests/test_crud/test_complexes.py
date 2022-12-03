from models.models import Complex


async def test_complex_create():
    data = {
        "description": "Описание комплекса 99",
        "name": "комплекс 99",
        "number": 99,
        "duration": 99
    }
    complex_data = Complex(**data)
    await complex_data.save()
    assert complex_data.id > 0


async def test_complex_get_by_id():
    complex_data = await Complex.get_by_id(1)
    assert complex_data is not None


async def test_complex_update():
    all_complexes: list[Complex] = await Complex.get_all()
    last_id: Complex = max(all_complexes, key=lambda x: x.id)
    complex_data: Complex = await Complex.get_by_id(last_id.id)
    assert complex_data.duration == 99
    complex_data.duration = 100
    new_data: Complex = await complex_data.save()
    assert new_data.duration == 100


async def test_get_next_complex():
    complex_data: Complex = await Complex.get_by_id(1)
    next_complex_id: int = await Complex.next_complex_id(complex_data)
    assert next_complex_id == 2


async def test_complex_delete():
    deleting_complexes: list[Complex] = await Complex.get_all()
    last_id: Complex = max(deleting_complexes, key=lambda x: x.id)
    complex_data = await Complex.delete_by_id(last_id.id)
    assert complex_data is None
