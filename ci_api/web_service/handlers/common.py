from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr
from starlette.requests import Request

from config import templates
from exc.exceptions import UserNotFoundError
from models.models import User
from schemas.user_schema import UserPhoneLogin
from services.web_context_class import WebContext
from services.user import check_phone_and_password_correct
from services.utils import generate_random_password
from web_service.utils.title_context_func import get_page_titles
from web_service.utils.get_contexts import (
    get_email_send_context, get_base_context, get_logged_user_context, update_user_session_token
)


async def user_login_via_phone(
        request: Request = None,
        context: dict = Depends(get_base_context),
        form_data: UserPhoneLogin = Depends(UserPhoneLogin.as_form)

) -> WebContext:

    web_context = WebContext(context=context)
    if user := await check_phone_and_password_correct(form_data):
        web_context.context.update(user=user)
        web_context.api_data.update(user=user)
        if not user.is_verified:
            web_context.template = 'forget2.html'

            return web_context
        await update_user_session_token(request, user)

        web_context.redirect = '/profile'

        return web_context

    web_context.error = "Invalid user or password"
    web_context.template = "entry_via_phone.html"
    web_context.to_raise = UserNotFoundError

    return web_context


async def restore_password(
        context: dict = Depends(get_base_context),
        email: EmailStr = Form(...),
):
    user: User = await User.get_by_email(email)
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
    user.password = await user.get_hashed_password(new_password)
    await user.save()
    context.update(success=f"Новый пароль выслан на почту {user.email}")
    return templates.TemplateResponse(
        "entry_sms.html", context=get_page_titles(context, "entry_sms.html"))


async def set_new_password(
        context: dict = Depends(get_logged_user_context),
        old_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
):
    user: User = context.get('user')

    context = get_page_titles(context, "edit_profile.html")
    if not await user.is_password_valid(old_password):
        context.update(error="Неверный пароль")
        return templates.TemplateResponse("edit_profile.html", context=context)

    if password == old_password:
        context.update(error="Новый пароль не должен совпадать со старым")
        return templates.TemplateResponse("edit_profile.html", context=context)

    if password != password2:
        context.update(error="Пароли не совпадают")
        return templates.TemplateResponse("edit_profile.html", context=context)

    context.update(success="Пароль успешно изменен.")
    user.password = await user.get_hashed_password(password)
    await user.save()

    return templates.TemplateResponse(
        "profile.html", context=get_page_titles(context, "profile.html"))
