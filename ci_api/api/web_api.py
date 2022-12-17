import base64

from fastapi import APIRouter, status, Depends, Body

from models.models import User, Complex
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
    """Return complexes list"""

    complexes: list[Complex] = await Complex.get_all()
    # TODO отправлять три списка - просмотренные, доступныЙ и недоступные
    return dict(user=UserOutput(**user.dict()), complexes=complexes)


@router.post("/set_avatar", status_code=204)
async def set_avatar(
        avatar: AvatarBase,
        user: User = Depends(get_user_from_context)
):
    logger.info(avatar)
    coded_string = avatar.as_bytes
    result = base64.b64decode(coded_string)
    logger.info(f'DECODED: {result}')
