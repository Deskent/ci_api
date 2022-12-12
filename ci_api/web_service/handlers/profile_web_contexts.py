from fastapi import Form, Depends
from loguru import logger
from pydantic import EmailStr

from models.models import User
from schemas.user_schema import slice_phone_to_format
from services.emails import send_verification_mail, EmailException
from services.web_context_class import WebContext
from web_service.utils.get_contexts import get_logged_user_context, get_user_from_context, \
    get_profile_page_context


async def get_edit_profile_web_context(
        username: str = Form(),
        last_name: str = Form(),
        third_name: str = Form(),
        email: EmailStr = Form(),
        phone: str = Form(),
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_from_context)
) -> WebContext:
    obj = WebContext(context=context)

    user.username = username
    user.last_name = last_name
    user.third_name = third_name
    phone: str = slice_phone_to_format(phone)
    if user.phone != phone:
        # TODO send sms to verify ?
        pass
    user.phone = phone
    if user.email != email:
        try:
            code: str = await send_verification_mail(email)
            logger.debug(f"Email code: {code}")
            user.email_code = code
            user.is_verified = False
            user.expired_at = None
            user.email = email
        except EmailException:
            obj.error = "Неверный адрес почты"
            obj.template = "edit_profile.html"

            return obj

    await user.save()
    obj.context = await get_profile_page_context(obj.context)
    obj.success = 'Профиль успешно изменен'
    obj.template = "profile.html"

    return obj
