from typing import Callable

from fastapi import Depends, Form
from loguru import logger
from starlette.requests import Request

from config import settings
from exc.exceptions import UserNotFoundError, SmsCodeNotValid
from models.models import User
from schemas.user_schema import slice_phone_to_format
from services.user import send_sms
from services.web_context_class import WebContext
from web_service.services.sms_class import sms_service, SMSException
from web_service.utils.get_contexts import get_base_context, update_user_session_token


async def entry_via_sms_or_call(
        context: dict = Depends(get_base_context),
        sms_send_to: str = Form(...),
        phone: str = Form(...),
) -> WebContext:
    web_context = WebContext(context=context)
    phone = slice_phone_to_format(phone)
    user: User = await User.get_by_phone(phone)
    if not user:
        web_context.error = "Пользователь с таким номером телефона не найден"
        web_context.template = "entry.html"
        return web_context

    web_context.context.update(user=user)
    if sms_send_to == "sms":
        web_context = await enter_via_sms(web_context, user)
    elif sms_send_to == "call":
        web_context = await enter_via_phone_call(web_context, user)
    return web_context


async def enter_via_phone_call(obj: WebContext, user: User) -> WebContext:
    try:
        code: str = await sms_service.send_call(phone=user.phone)
        if code:
            user.sms_call_code = str(code)
            await user.save()
            obj.template = "forget3.html"

    except SMSException as err:
        logger.error(err)
        obj.error = str(err)
        obj.template = "entry_sms.html"

    return obj


async def enter_via_sms(obj: WebContext, user: User) -> WebContext:

    result: dict = await send_sms(user.phone)
    if sms_message := result.get('sms_message'):
        user.sms_message = sms_message
        await user.save()
    elif error := result.get('error'):
        obj.error = error

    obj.template = "forget2.html"
    if settings.STAGE == 'test':
        obj.success = f'Тестовый режим: ваш код: {sms_message}'
    return obj


async def approve_sms_code(
        context: dict,
        code: str,
        request: Request = None,
        user_id: int = None,
        phone: str = None,
) -> WebContext:

    obj = WebContext(context=context)

    user: User | None = None
    if user_id:
        user: User = await User.get_by_id(user_id)
    elif phone:
        user: User = await User.get_by_phone(phone)

    if not user:
        obj.error = "Неверный номер телефона"
        obj.template = "entry.html"
        obj.to_raise = UserNotFoundError

        return obj

    obj.context.update(user=user)
    obj.api_data.update(payload=user)
    user_code: str = user.sms_message
    cleaner: Callable = user.clean_sms_code
    if request.url.path == "/forget3":
        user_code: str = user.sms_call_code
        cleaner: Callable = user.clean_sms_call_code

    if code != user_code:
        obj.error = f"Неверный код: {code}"
        logger.debug(obj.error)
        url_path = f"{request.url.path}.html"
        obj.template = url_path
        obj.to_raise = SmsCodeNotValid
        return obj

    await cleaner()
    await user.set_verified()
    await update_user_session_token(request, user)
    obj.template = "profile.html"

    return obj
