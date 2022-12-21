from loguru import logger

from crud_class.crud import CRUD
from exc.exceptions import EmailError
from exc.register import SmsServiceError, PhoneExistsError, EmailExistsError
from models.models import User
from schemas.user_schema import slice_phone_to_format, UserEditProfile
from services.emails import send_verification_mail, EmailException
from services.user import send_sms, check_user_phone_exists, check_email_exists
from misc.web_context_class import WebContext


async def update_web_context_with_phone(
        web_context: WebContext, user_data: UserEditProfile, user: User
) -> tuple[WebContext, User]:
    """Check user phone exists, send sms to new phone, update web_context and user
    Not updating web_context template
    """
    logger.debug(f"Check phone exists {user_data}")
    if await check_user_phone_exists(user_data.phone):
        web_context.error = PhoneExistsError.detail
        web_context.to_raise = PhoneExistsError

        return web_context, user

    result: dict = await send_sms(user_data.phone)
    if sms_message := result.get('sms_message'):
        logger.debug(f"Sms_message code: {sms_message}")
        user.sms_message = sms_message
        user.phone = user_data.phone

    elif error := result.get('error'):
        web_context.error = error
        web_context.to_raise = SmsServiceError

    return web_context, user


async def update_web_context_with_email(
        web_context: WebContext, user_data: UserEditProfile, user: User
) -> tuple[WebContext, User]:
    """Check user email exists, send code to new email,
    update web_context and user
    Not updating web_context template
    """

    logger.debug(f"Check email exists {user_data}")

    if await check_email_exists(user_data.email):
        web_context.error = EmailExistsError.detail
        web_context.to_raise = EmailExistsError

        return web_context, user
    try:
        code: str = await send_verification_mail(user_data.email)
        logger.debug(f"Email code: {code}")
        user.email_code = code
        user.is_verified = False
        user.expired_at = None
        user.email = user_data.email
    except EmailException:
        web_context.error = "Неверный адрес почты"
        web_context.to_raise = EmailError

    return web_context, user


async def _check_phone_changed(
        web_context: WebContext, user_data: UserEditProfile, user: User
) -> tuple[WebContext, User]:
    """Check user phone changed"""

    logger.debug(f"Check phone changed {user_data}")

    if user_data.phone:
        phone: str = slice_phone_to_format(user_data.phone)
        if user.phone != phone:
            web_context, user = await update_web_context_with_phone(web_context, user_data, user)
            web_context.template = 'forget2.html'

    return web_context, user


async def _check_email_changed(
        web_context: WebContext, user_data: UserEditProfile, user: User
) -> tuple[WebContext, User]:
    """Check user email changed"""

    logger.debug(f"Check email changed {user_data}")
    if user_data.email and user.email != user_data.email:
        web_context, user = await update_web_context_with_email(web_context, user_data, user)

    return web_context, user


async def get_edit_profile_web_context(
        context: dict,
        user_data: UserEditProfile,
        user: User
) -> WebContext:

    web_context = WebContext(context=context)
    if user_data.username:
        user.username = user_data.username
    if user_data.last_name:
        user.last_name = user_data.last_name
    if user_data.third_name:
        user.third_name = user_data.third_name

    web_context, user = await _check_phone_changed(web_context, user_data, user)
    if web_context.error:
        web_context.template = "edit_profile.html"
        return web_context

    web_context, user = await _check_email_changed(web_context, user_data, user)
    if web_context.error:
        web_context.template = "edit_profile.html"
        return web_context

    user = await CRUD.user.save(user)
    web_context.context.update(user=user)
    web_context.api_data.update(payload=user)
    web_context.success = 'Профиль успешно изменен'
    if not web_context.template:
        web_context.template = "profile.html"

    return web_context
