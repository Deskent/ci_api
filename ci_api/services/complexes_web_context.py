from crud_class.crud import CRUD
from database.models import User, Complex
from misc.web_context_class import WebContext
from schemas.complexes_videos import UserComplexesState
from schemas.user_schema import UserOutput
from services.utils import convert_to_minutes


def _convert_duration_from_int_to_time(data: list[Complex]) -> list[Complex]:
    """Convert complex duration from int to time format"""

    for elem in data:
        elem.duration = convert_to_minutes(elem.duration)

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
    """Return user complexes state"""

    web_context = WebContext(context)
    web_context.context.update(user=user)

    today_complex: dict = {}
    if not await CRUD.viewed_complex.is_last_viewed_today(user.id):
        today_complex: Complex = await CRUD.complex.get_by_id(user.current_complex)
        today_complex.duration = convert_to_minutes(today_complex.duration)

    complexes: list[Complex] = await CRUD.complex.get_all()
    user_viewed_complexes: list[
        int] = await CRUD.viewed_complex.get_all_viewed_complexes_ids(user.id)
    viewed_complexes: list[Complex] = _get_viewed_complexes(complexes, user_viewed_complexes)
    not_viewed_complexes: list[
        Complex] = _get_not_viewed_complexes(complexes, user_viewed_complexes)

    # TODO убрать возврат пользователя после реализации фронта
    result = UserComplexesState(
        user=UserOutput(**user.dict()),
        viewed_complexes=viewed_complexes,
        today_complex=today_complex,
        not_viewed_complexes=not_viewed_complexes
    )
    web_context.api_data.update(payload=result)

    return web_context


async def get_all_complexes_web_context(
        context: dict
) -> WebContext:
    """Return all complexes with duration in minutes, not time"""

    web_context = WebContext(context)
    complexes: list[Complex] = await CRUD.complex.get_all()
    for complex_ in complexes:
        complex_.duration = convert_to_minutes(complex_.duration)

    web_context.context.update(complexes=complexes)
    web_context.api_data.update(payload=complexes)
    web_context.template = "complexes_list.html"

    return web_context
