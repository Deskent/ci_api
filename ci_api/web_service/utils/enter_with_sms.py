import random
from typing import Optional

from fastapi import Depends, Form
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from config import templates
from database.db import get_db_session
from models.models import User
from web_service.sms_utils import sms_service, SMSException
from web_service.utils.context_utils import get_context, login_user


def generate_sms_message() -> str:
    return "".join(
        (str(random.randint(0, 9)) for _ in range(4))
    )


async def _send_sms(user, session, context):
    message: str = generate_sms_message()
    logger.debug(f"Sms message generated: {message}")
    try:
        sms_id: str = await sms_service.send_sms(message)
        if sms_id:
            user.sms_message = message
            await user.save(session)
    except SMSException as err:
        logger.error(err)
        context.update(error=err, user=user)
    return templates.TemplateResponse("forget2.html", context=context)


async def _send_call(user, session, context):
    try:
        code: str = await sms_service.send_call()
        if code:
            user.sms_call_code = code
            await user.save(session)
    except SMSException as err:
        logger.error(err)
        context.update(error=err, user=user)
    return templates.TemplateResponse("forget3.html", context=context)


async def enter_by_sms(
        context: dict = Depends(get_context),
        sms_send_to: str = Form(...),
        phone: str = Form(...),
        session: AsyncSession = Depends(get_db_session),
):
    user: User = await User.get_by_phone(session, phone)
    if not user:
        context.update(error="User with this phone number not found")
        return templates.TemplateResponse("entry.html", context=context)

    context.update(user=user)
    if sms_send_to == "sms":
        return await _send_sms(user, session, context)

    elif sms_send_to == "call":
        return await _send_call(user, session, context)


async def approve_sms_code(
        request: Request,
        context: dict = Depends(get_context),
        sms_input_1: Optional[str] = Form(...),
        sms_input_2: Optional[str] = Form(...),
        sms_input_3: Optional[str] = Form(...),
        sms_input_4: Optional[str] = Form(...),
        user_id: Optional[int] = Form(...),
        session: AsyncSession = Depends(get_db_session),
):
    code = ''.join((sms_input_1, sms_input_2, sms_input_3, sms_input_4))
    user: User = await User.get_by_id(session, user_id)
    if not user:
        context.update(error="User with this phone number not found")
        return templates.TemplateResponse("entry.html", context=context)

    user_code: str = user.sms_message
    if request.url.path == "forget3":
        user_code: str = user.sms_call_code
    if code != user_code:
        logger.debug("Wrong sms code")
        context.update(error="Wrong sms code", user=user)
        return templates.TemplateResponse(f"{request.url.path}.html", context=context)

    await clean_sms_code(user, session)

    return await login_user(user, request)


async def clean_sms_code(user, session):
    user.sms_message = None
    await user.save(session)
