from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr
from starlette.requests import Request

from config import templates
from exc.exceptions import UserNotFoundErrorApi
from database.models import User
from schemas.user_schema import UserPhoneLogin
from crud_class.crud import CRUD
from misc.web_context_class import WebContext
from services.user import check_phone_and_password_correct
from services.utils import generate_random_password
from web_service.handlers.enter_with_sms import update_user_token_to_web_context
from web_service.utils.title_context_func import get_page_titles
from web_service.utils.get_contexts import (
    get_email_send_context, get_base_context, update_user_session_token
)


async def user_login_via_phone(
        request: Request = None,
        context: dict = Depends(get_base_context),
        form_data: UserPhoneLogin = Depends(UserPhoneLogin.as_form)

) -> WebContext:

    web_context = WebContext(context=context)
    if user := await check_phone_and_password_correct(form_data):
        web_context.context.update(user=user)
        web_context.api_data.update(payload=user)
        if not user.is_verified:
            web_context.error = 'Пользователь не верифицирован'
            web_context.template = 'forget2.html'

            return web_context
        await update_user_session_token(request, user)

        web_context.redirect = '/profile'

        return web_context

    web_context.error = UserNotFoundErrorApi.detail
    web_context.template = "entry_via_phone.html"
    web_context.to_raise = UserNotFoundErrorApi

    return web_context


async def restore_password(
        context: dict = Depends(get_base_context),
        email: EmailStr = Form(...),
):
    user: User = await CRUD.user.get_by_email(email)
    if not user:
        context.update(error='Неверный адрес почты')
        return templates.TemplateResponse(
            "forget1.html", context=get_page_titles(context, "forget1.html"))

    new_password: str = generate_random_password()
    email_errors: dict = await get_email_send_context(user.email, new_password)
    if email_errors:
        context.update(email_errors)

        return templates.TemplateResponse(
            "forget1.html", context=get_page_titles(context, "forget1.html"))

    logger.debug(f"New password: {new_password}")
    user.password = await CRUD.user.get_hashed_password(new_password)
    await CRUD.user.save(user)
    context.update(success=f"Новый пароль выслан на почту {user.email}")

    return templates.TemplateResponse(
        "entry_sms.html", context=get_page_titles(context, "entry_sms.html"))


async def set_new_password(
        context: dict,
        old_password: str,
        password: str,
        password2: str,
):
    user: User = context.get('user')
    web_context = WebContext(context)
    web_context.template = "edit_profile.html"
    if not await CRUD.user.is_password_valid(user, old_password):
        web_context.error = "Неверный пароль"

        return web_context

    if password == old_password:
        web_context.error = "Новый пароль не должен совпадать со старым"

        return web_context

    if password != password2:
        web_context.error = "Пароли не совпадают"

        return web_context

    web_context.success = "Пароль успешно изменен."
    user.password = await CRUD.user.get_hashed_password(password)
    await CRUD.user.save(user)
    web_context.template = "profile.html"
    web_context: WebContext = await update_user_token_to_web_context(web_context)

    return web_context
