from loguru import logger

from exc.exceptions import EmailError
from exc.register import SmsServiceError, PhoneExistsError, EmailExistsError
from models.models import User
from schemas.user_schema import slice_phone_to_format, UserEditProfile
from services.emails import send_verification_mail, EmailException
from services.user import send_sms, check_user_phone_exists, check_email_exists
from services.web_context_class import WebContext


async def get_edit_profile_web_context(
        context: dict,
        user_data: UserEditProfile,
        user: User
) -> WebContext:
    web_context = WebContext(context=context)

    user.username = user_data.username
    user.last_name = user_data.last_name
    user.third_name = user_data.third_name
    phone: str = slice_phone_to_format(user_data.phone)
    if user.phone != phone:

        if await check_user_phone_exists(user_data.phone):
            web_context.error = PhoneExistsError.detail
            web_context.template = "edit_profile.html"
            web_context.to_raise = PhoneExistsError
            return web_context

        result: dict = await send_sms(user_data.phone)
        if sms_message := result.get('sms_message'):
            logger.debug(f"Sms_message code: {sms_message}")
            user.sms_message = sms_message
        elif error := result.get('error'):
            web_context.error = error
            web_context.template = "edit_profile.html"
            web_context.to_raise = SmsServiceError

            return web_context

    user.phone = phone
    if user.email != user_data.email:
        if await check_email_exists(user_data.email):
            web_context.error = EmailExistsError.detail
            web_context.template = "edit_profile.html"
            web_context.to_raise = EmailExistsError

            return web_context
        try:
            code: str = await send_verification_mail(user_data.email)
            logger.debug(f"Email code: {code}")
            user.email_code = code
            user.is_verified = False
            user.expired_at = None
            user.email = user_data.email
        except EmailException:
            web_context.error = "Неверный адрес почты"
            web_context.template = "edit_profile.html"
            web_context.to_raise = EmailError

            return web_context

    user = await user.save()
    web_context.context.update(user=user)
    web_context.api_data.update(payload=user)
    web_context.success = 'Профиль успешно изменен'
    web_context.template = "forget2.html"

    return web_context
