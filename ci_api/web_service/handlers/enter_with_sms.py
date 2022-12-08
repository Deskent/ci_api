from typing import Optional

from fastapi import Depends, Form
from loguru import logger
from starlette.requests import Request

from config import templates
from models.models import User
from services.user import send_sms
from web_service.services.sms_class import sms_service, SMSException
from web_service.utils.title_context_func import update_title
from web_service.utils.get_contexts import get_base_context


async def _send_call(user: User, context: dict):
    try:
        code: str = await sms_service.send_call(phone=user.phone)
        if code:
            user.sms_call_code = str(code)
            await user.save()
            return templates.TemplateResponse("forget3.html", context=update_title(context, "forget3.html"))
    except SMSException as err:
        logger.error(err)
        context.update(error=err, user=user)
    return templates.TemplateResponse("entry_sms.html", context=update_title(context, "entry_sms.html"))


async def enter_by_sms(
        context: dict = Depends(get_base_context),
        sms_send_to: str = Form(...),
        phone: str = Form(...),
):
    user: User = await User.get_by_phone(phone)
    if not user:
        context.update(error="User with this phone number not found")
        return templates.TemplateResponse(
            "entry.html", context=update_title(context, "entry.html")
        )

    context.update(user=user)
    if sms_send_to == "sms":
        result: dict = await send_sms(user.phone)
        if sms_message := result.get('sms_message'):
            user.sms_message = sms_message
            await user.save()
        elif result.get('error'):
            context.update(**result, user=user)

        return templates.TemplateResponse(
            "forget2.html", context=update_title(context, "forget2.html"))

    elif sms_send_to == "call":
        return await _send_call(user, context)


async def approve_sms_code(
        request: Request,
        context: dict = Depends(get_base_context),
        sms_input_1: Optional[str] = Form(...),
        sms_input_2: Optional[str] = Form(...),
        sms_input_3: Optional[str] = Form(...),
        sms_input_4: Optional[str] = Form(...),
        user_id: Optional[int] = Form(...),
):
    code = ''.join((sms_input_1, sms_input_2, sms_input_3, sms_input_4))
    user: User = await User.get_by_id(user_id)
    if not user:
        context.update(error="Неверный номер телефона")
        return templates.TemplateResponse("entry.html", context=update_title(context, "entry"))

    user_code: str = user.sms_message
    if request.url.path == "/forget3":
        user_code: str = user.sms_call_code
    if code != user_code:
        text = f"Неверный код: {code}"
        logger.debug(text)
        context.update(error=text, user=user)
        url_path = f"{request.url.path}.html"
        return templates.TemplateResponse(url_path, context=update_title(context, url_path))

    await user.clean_sms_code()
    user.is_verified = True
    await user.save()

    context.update(user=user)
    return templates.TemplateResponse(
            "profile.html", context=update_title(context, "profile.html"))
