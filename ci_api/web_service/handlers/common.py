from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import templates
from models.models import User
from schemas.user import UserLogin
from services.user import user_login, get_bearer_header
from services.utils import generate_random_password
from web_service.utils.title_context_func import update_context_title
from web_service.utils.titles_context import get_profile_context, get_session_context, \
    get_email_send_context, get_password_recovery_context


async def user_entry(
        request: Request,
        context: dict = Depends(get_profile_context),
        form_data: UserLogin = Depends(UserLogin.as_form)

) -> templates.TemplateResponse:
    if user := await user_login(form_data):
        context.update(user=user)
        if not user.is_verified:
            return templates.TemplateResponse(
                "check_email.html", context=update_context_title(context, 'check_email'))

        login_token: str = await user.get_user_token()
        headers: dict[str, str] = get_bearer_header(login_token)
        request.session.update(token=login_token)

        return RedirectResponse('/profile', headers=headers)

    error = "Invalid user or password"
    context.update(error=error)

    return templates.TemplateResponse("entry.html", context=update_context_title(context, 'entry'))


async def load_self_page(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
) -> templates.TemplateResponse:
    if not session_context:
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, 'entry'))

    context.update(**session_context)
    page_name: str = context['request'].url.path[1:] + '.html'

    return templates.TemplateResponse(page_name, context=update_context_title(context, page_name))


async def restore_password(
        context: dict = Depends(get_password_recovery_context),
        email: EmailStr = Form(...),
):
    user: User = await User.get_by_email(email)
    if not user:
        context.update(error='Неверный адрес почты')
        return templates.TemplateResponse(
            "forget1.html", context=update_context_title(context, "forget1.html"))

    new_password: str = generate_random_password()
    email_errors: dict = await get_email_send_context(user.email, new_password)
    if email_errors:
        context.update(email_errors)
        return templates.TemplateResponse(
            "forget1.html", context=update_context_title(context, "forget1.html"))

    logger.debug(f"New password: {new_password}")
    user.password = await user.get_hashed_password(new_password)
    await user.save()
    context.update(success=f"Новый пароль выслан на почту {user.email}")
    return templates.TemplateResponse(
        "entry.html", context=update_context_title(context, "entry.html"))


async def set_new_password(
        context: dict = Depends(get_profile_context),
        session_context: dict = Depends(get_session_context),
        old_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
):
    user: User = session_context.get('user')
    if not user:
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, "entry.html"))

    context.update(**session_context)
    context = update_context_title(context, "edit_profile.html")
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
        "profile.html", context=update_context_title(context, "profile.html"))
