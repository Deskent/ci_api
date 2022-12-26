from fastapi import APIRouter, Depends, status

from crud_class.crud import CRUD
from database.models import User, Complex, Video
from exc.exceptions import ComplexNotFoundError
from misc.web_context_class import WebContext
from schemas.complexes_videos import ComplexData, ComplexesListWithViewedAndNot
from services.complexes_web_context import get_complexes_list_web_context, \
    get_all_complexes_web_context
from services.depends import get_logged_user
from services.videos_methods import get_viewed_complex_response

router = APIRouter(prefix="/complex", tags=['Complexes'])


# @router.get("/", response_model=UserProgress)
# async def current_progress(
#         user: User = Depends(get_logged_user)
# ):
#     """
#     Return current user views progress
#     """
#     return user


@router.get("/state", response_model=ComplexesListWithViewedAndNot)
async def get_complexes_list_api(
        user: User = Depends(get_logged_user)
):
    """Return user state of viewed_complexes, today_complex, not_viewed_complexes"""

    web_context: WebContext = await get_complexes_list_web_context({}, user)
    return web_context.api_render()


@router.get(
    "/all",
    response_model=list[Complex],
    dependencies=[Depends(get_logged_user)]
)
async def get_all_complexes_api():
    """Return all complexes as JSON"""

    web_context: WebContext = await get_all_complexes_web_context({})
    return web_context.api_render()


@router.get(
    "/{complex_id}",
    response_model=ComplexData,
    dependencies=[Depends(get_logged_user)]
)
async def complex_data(
        complex_id: int,
):
    """Return complex info"""

    if not (complex_ := await CRUD.complex.get_by_id(complex_id)):
        raise ComplexNotFoundError
    videos: list[Video] = await CRUD.video.get_all_by_complex_id(complex_id)

    return ComplexData(**complex_.dict(), videos=videos)


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed_api(
        complex_id: int,
        user: User = Depends(get_logged_user)
):
    """
    Checks complex was viewed and user get new level. Need authorization.

    :param complex_id: integer - Viewed complex ID

    :return: JSON like: {"level_up": False} or
    {"level_up": False, "new_level": user.level, "next_complex_duration": next_complex_duration}
    """

    return await get_viewed_complex_response(user=user, complex_id=complex_id)
