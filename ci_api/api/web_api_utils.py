from fastapi import UploadFile
from loguru import logger

import services.utils
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
    file_path = settings.MEDIA_DIR / 'avatars' / file.filename
    if file_path.exists():
        random_symbols: str = services.utils.generate_four_random_digits_string()
        file_path = settings.MEDIA_DIR / 'avatars' / f"{random_symbols}_{file.filename}"

    save_uploaded_file(file_path, file)
    avatar: Avatar = await Avatar.create(data=dict(file_name=file_path.name))
    logger.info(avatar)
    user.avatar = avatar.id
    await user.save()
    web_context.context.update(user=user, avatar=avatar)
    web_context.api_data.update(payload=dict(user=user, avatar=avatar))

    return web_context
