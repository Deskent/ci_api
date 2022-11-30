import pytest

from models.models import Complex


@pytest.fixture
def get_complex_data() -> dict:
    return {
               "description": "Описание комплекса 1",
               "name": "комплекс 1",
               "number": 999,
               "next_complex_id": 2,
               "duration": 0
           }


@pytest.mark.skip
async def test_add_complex(db_session, get_complex_data):
    new_complex = await Complex.add_new(session=db_session, **get_complex_data)
    assert new_complex.id
    await new_complex.delete(session=db_session)
