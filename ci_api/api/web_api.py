import base64

from fastapi import APIRouter, status, Depends, Body

from models.models import User, Complex, ViewedComplex
from schemas.avatar import AvatarBase
from schemas.user_schema import UserOutput
from services.videos_methods import get_viewed_complex_response
from web_service.utils.get_contexts import get_user_from_context
from config import logger

router = APIRouter(prefix="/web", tags=['WebApi'])


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed_web(
        complex_id: int,
        user: User = Depends(get_user_from_context)
):
    return await get_viewed_complex_response(user=user, complex_id=complex_id)


@router.get("/complex/list", response_model=dict)
async def get_complexes_list_web(
        user: User = Depends(get_user_from_context)
):
    """Return viewed_complexes, today_complex, not_viewed_complexes, user"""

    today_complex = None
    if not await ViewedComplex.is_last_viewed_today(user.id):
        today_complex: Complex | None = await Complex.get_by_id(user.id)
    complexes: list[Complex] = await Complex.get_all()
    user_viewed_complexes: list[int] = await ViewedComplex.get_all_viewed_complexes_ids(user.id)
    viewed_complexes: list[Complex] = [
        elem
        for elem in complexes
        if elem.id in user_viewed_complexes

    ]
    not_viewed_complexes: list[Complex] = [
        elem
        for elem in complexes
        if elem.id not in user_viewed_complexes

    ]

    return dict(
        user=UserOutput(**user.dict()),
        viewed_complexes=viewed_complexes,
        today_complex=today_complex,
        not_viewed_complexes=not_viewed_complexes
    )


@router.post("/set_avatar", status_code=204)
async def set_avatar(
        avatar: AvatarBase,
        user: User = Depends(get_user_from_context)
):
    logger.info(avatar)
    coded_string = avatar.as_bytes
    result = base64.b64decode(coded_string)
    logger.info(f'DECODED: {result}')
