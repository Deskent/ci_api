import base64

from fastapi import APIRouter, status, Depends, Request, UploadFile, HTTPException

from admin.utils import save_uploaded_file
from config import logger, settings
from models.models import User, Avatar
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


async def set_avatar_from_file_web_context(
    context: dict,
    user: User
):
    pass


@router.post("/upload_avatar_as_file", status_code=status.HTTP_202_ACCEPTED)
async def upload_avatar_as_file(
        request: Request
        # file: UploadFile,
        # user: User = Depends(get_user_from_context)
):
    logger.info(await request.body())
    # file_path = settings.MEDIA_DIR / 'avatars' /file.filename
    # if file_path.exists():
    #     error_text = f'File with name {file_path} exists.'
    #     logger.warning(error_text)
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=error_text
    #     )
    # save_uploaded_file(file_path, file)
    # avatar: Avatar = await Avatar.create(data=dict(file_name=str(file.filename)))
    # logger.info(avatar)
    # user.avatar = avatar.id
    # await user.save()


@router.post("/upload_avatar_as_string", status_code=status.HTTP_202_ACCEPTED)
async def upload_avatar_as_string(
        request: Request,
        # user: User = Depends(get_user_from_context)
):
    logger.info(f"BODY: {await request.body()}")
    # coded_string = avatar.as_bytes
    # result = base64.b64decode(coded_string)
    # logger.info(f'DECODED: {result}')
