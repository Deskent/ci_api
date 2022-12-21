import datetime

from fastapi import UploadFile
from loguru import logger

from admin.utils import save_uploaded_file
from config import settings
from crud_class.crud import CRUD
from models.models import User, Avatar
from misc.web_context_class import WebContext


async def set_avatar_from_file_web_context(
        context: dict,
        user: User,
        file: UploadFile
):
    web_context = WebContext(context)
    file_path = settings.MEDIA_DIR / 'avatars' / file.filename
    if file_path.exists():
        random_symbols = int(datetime.datetime.now().timestamp())
        file_path = settings.MEDIA_DIR / 'avatars' / f"{random_symbols}_{file.filename}"

    save_uploaded_file(file_path, file)
    avatar: Avatar = await CRUD.avatar.create(data=dict(file_name=file_path.name))
    logger.info(avatar)
    await CRUD.user.set_avatar(avatar.id, user=user)
    web_context.context.update(user=user, avatar=avatar)
    web_context.api_data.update(payload=dict(user=user, avatar=avatar))

    return web_context
