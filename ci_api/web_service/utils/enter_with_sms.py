from typing import Optional

from fastapi import Depends, Form
from loguru import logger
from starlette.requests import Request

from config import templates
from models.models import User
from services.utils import generate_four_random_digits_string
from web_service.sms_utils import sms_service, SMSException
from web_service.utils.context_utils import get_context, login_user


async def _send_sms(user, context):
    message: str = generate_four_random_digits_string()
    logger.debug(f"Sms message generated: {message}")
    try:
        sms_id: str = await sms_service.send_sms(phone=user.phone, message=message)
        if sms_id:
            user.sms_message = message
            await user.save()
    except SMSException as err:
        logger.error(err)
        context.update(error=err, user=user)
    return templates.TemplateResponse("entry_sms.html", context=context)


async def _send_call(user, context):
    try:
        code: str = await sms_service.send_call(phone=user.phone)
        if code:
            user.sms_call_code = str(code)
            await user.save()
            return templates.TemplateResponse("forget3.html", context=context)
    except SMSException as err:
        logger.error(err)
        context.update(error=err, user=user)
    return templates.TemplateResponse("entry_sms.html", context=context)


async def enter_by_sms(
        context: dict = Depends(get_context),
        sms_send_to: str = Form(...),
        phone: str = Form(...),
):
    user: User = await User.get_by_phone(phone)
    if not user:
        context.update(error="User with this phone number not found")
        return templates.TemplateResponse("entry.html", context=context)

    context.update(user=user)
    if sms_send_to == "sms":
        return await _send_sms(user, context)

    elif sms_send_to == "call":
        return await _send_call(user, context)


async def approve_sms_code(
        request: Request,
        context: dict = Depends(get_context),
        sms_input_1: Optional[str] = Form(...),
        sms_input_2: Optional[str] = Form(...),
        sms_input_3: Optional[str] = Form(...),
        sms_input_4: Optional[str] = Form(...),
        user_id: Optional[int] = Form(...),
):
    code = ''.join((sms_input_1, sms_input_2, sms_input_3, sms_input_4))
    user: User = await User.get_by_id(user_id)
    if not user:
        context.update(error="User with this phone number not found")
        return templates.TemplateResponse("entry.html", context=context)

    user_code: str = user.sms_message
    if request.url.path == "/forget3":
        user_code: str = user.sms_call_code
    if code != user_code:
        logger.debug("Wrong sms code")
        context.update(error="Wrong sms code", user=user)
        return templates.TemplateResponse(f"{request.url.path}.html", context=context)

    await clean_sms_code(user)

    return await login_user(user, request)


async def clean_sms_code(user):
    user.sms_message = None
    await user.save()
