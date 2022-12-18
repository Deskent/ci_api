import base64

from fastapi import APIRouter, status, Depends, Request

from config import logger
from models.models import User
from schemas.avatar import AvatarBase
from schemas.complexes_videos import ComplexesListWithViewedAndNot
from services.complexes_web_context import get_complexes_list_web_context
from services.videos_methods import get_viewed_complex_response
from services.web_context_class import WebContext
from web_service.utils.get_contexts import get_user_from_context

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


@router.get("/complex/list", response_model=ComplexesListWithViewedAndNot)
async def get_complexes_list_web(
        user: User = Depends(get_user_from_context)
):
    """Return viewed_complexes, today_complex, not_viewed_complexes, user"""

    web_context: WebContext = await get_complexes_list_web_context({}, user)
    return web_context.api_render()


@router.post("/upload_avatar_as_file", status_code=status.HTTP_202_ACCEPTED)
async def set_avatar(
        request: Request,
        # user: User = Depends(get_user_from_context)
):
    form = await request.form()
    logger.info(form)


@router.post("/upload_avatar_as_string", status_code=status.HTTP_202_ACCEPTED)
async def set_avatar(
        request: Request,
        # user: User = Depends(get_user_from_context)
):
    logger.info(f"BODY: {await request.body()}")
    # coded_string = avatar.as_bytes
    # result = base64.b64decode(coded_string)
    # logger.info(f'DECODED: {result}')
