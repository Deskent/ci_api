from typing import Iterable

from models.models import User, Complex, ViewedComplex
from schemas.complexes_videos import ComplexesListWithViewedAndNot
from schemas.user_schema import UserOutput
from services.models_cache.crud import CRUD
from services.utils import convert_seconds_to_time
from services.web_context_class import WebContext

def _convert_duration_from_int_to_time(data: Iterable) -> Iterable:
    """Convert complex duration from int to time format"""

    for elem in data:
        elem.duration = convert_seconds_to_time(elem.duration)

    return data


def _get_viewed_complexes(
        complexes: list[Complex],
        user_viewed_complexes: list[int]
) -> list[Complex]:
    data: list[Complex] = [
        elem
        for elem in complexes
        if elem.id in user_viewed_complexes

    ]
    return _convert_duration_from_int_to_time(data)

def _get_not_viewed_complexes(
        complexes: list[Complex],
        user_viewed_complexes: list[int]
) -> list[Complex]:
    data: list[Complex] = [
        elem
        for elem in complexes
        if elem.id not in user_viewed_complexes

    ]
    return _convert_duration_from_int_to_time(data)


async def get_complexes_list_web_context(
        context: dict,
        user: User
):
    web_context = WebContext(context)
    web_context.context.update(user=user)

    today_complex = {}
    if not await ViewedComplex.is_last_viewed_today(user.id):
        today_complex: Complex = await CRUD.complex.get_by_id(user.current_complex)
        today_complex.duration = convert_seconds_to_time(today_complex.duration)

    complexes: list[Complex] = await CRUD.complex.get_all()
    user_viewed_complexes: list[int] = await ViewedComplex.get_all_viewed_complexes_ids(user.id)
    viewed_complexes: list[Complex] = _get_viewed_complexes(complexes, user_viewed_complexes)
    not_viewed_complexes: list[Complex] = _get_not_viewed_complexes(complexes, user_viewed_complexes)

    result = ComplexesListWithViewedAndNot(
        user=UserOutput(**user.dict()),
        viewed_complexes=viewed_complexes,
        today_complex=today_complex,
        not_viewed_complexes=not_viewed_complexes
    )
    web_context.api_data.update(payload=result)

    return web_context
