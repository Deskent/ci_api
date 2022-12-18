from fastapi import UploadFile, HTTPException
from loguru import logger
from starlette import status

from admin.utils import save_uploaded_file
from config import settings
from models.models import User, Avatar
from services.web_context_class import WebContext


async def set_avatar_from_file_web_context(
    context: dict,
    user: User,
    file: UploadFile
):
    web_context = WebContext(context)
    file_path = settings.MEDIA_DIR / 'avatars' /file.filename
    if file_path.exists():
        error_text = f'File with name {file_path} exists.'
        web_context.error = error_text
        web_context.to_raise = HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_text
        )
        logger.warning(error_text)
        return web_context

    save_uploaded_file(file_path, file)
    avatar: Avatar = await Avatar.create(data=dict(file_name=str(file.filename)))
    logger.info(avatar)
    user.avatar = avatar.id
    await user.save()
    web_context.context.update(user=user)
    web_context.api_data.update(payload=user)

    return web_context
