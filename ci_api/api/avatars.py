from fastapi import APIRouter, Depends, UploadFile
from loguru import logger
from starlette import status

from api.web_api_utils import set_avatar_from_file_web_context
from crud_class.crud import CRUD
from database.models import User, Avatar
from misc.web_context_class import WebContext
from services.depends import get_logged_user

router = APIRouter(prefix="/avatars", tags=['Avatars'])


@router.get(
    "/get_user_avatar",
    response_model=Avatar,
    status_code=status.HTTP_200_OK,
)
async def get_user_avatar(
        user: User = Depends(get_logged_user),
):
    """Return user avatar info. Need authorization.

    :return: Avatar as JSON
    """

    return await CRUD.avatar.get_by_id(user.avatar)


@router.post(
    "/upload_avatar_file",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_avatar_as_file(
        file: UploadFile,
        user: User = Depends(get_logged_user)
):
    """Set avatar for user

    :return: null
    """

    logger.debug(f"File received: {file.filename}")
    web_context: WebContext = await set_avatar_from_file_web_context(
        context={}, user=user, file=file)
    return web_context.api_render()
