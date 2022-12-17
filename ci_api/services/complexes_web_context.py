from models.models import User, Complex, ViewedComplex
from schemas.complexes_videos import ComplexesListWithViewedAndNot
from schemas.user_schema import UserOutput
from services.models_cache.base_cache import AllCache
from services.web_context_class import WebContext


def _get_viewed_complexes(
        complexes: list[Complex],
        user_viewed_complexes: list[int]
) -> list[Complex]:
    return [
        elem
        for elem in complexes
        if elem.id in user_viewed_complexes

    ]

def _get_not_viewed_complexes(
        complexes: list[Complex],
        user_viewed_complexes: list[int]
) -> list[Complex]:
    return [
        elem
        for elem in complexes
        if elem.id not in user_viewed_complexes

    ]

async def get_complexes_list_web_context(
        context: dict,
        user: User
):
    web_context = WebContext(context)
    web_context.context.update(user=user)

    today_complex = {}
    if not await ViewedComplex.is_last_viewed_today(user.id):
        today_complex: Complex = await AllCache.get_by_id(Complex, user.current_complex)

    complexes: list[Complex] = await AllCache.get_all(Complex)
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
