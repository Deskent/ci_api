import pytest

from crud_class.crud import CRUD
from database.models import Mood


@pytest.fixture
async def get_mood():
    data = {
        'name': 'test',
        'code': 'U+1F970'
    }
    mood: Mood = await CRUD.mood.create(data)
    yield mood
    await CRUD.mood.delete(mood)


async def test_crud_get_all_moods():
    moods: list[Mood] = await CRUD.mood.get_all()
    assert moods[0] is not None
    assert 'U+' not in moods[0].code
    assert '0x' in moods[0].code


async def test_get_mood_by_id(get_mood):
    mood: Mood = await CRUD.mood.get_by_id(get_mood.id)
    assert mood.id == get_mood.id
    assert 'U+' not in mood.code
    assert '0x' in mood.code
