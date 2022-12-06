from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from config import templates, logger
from models.models import User
from services.emails import send_verification_mail, EmailException
from web_service.utils.title_context_func import update_title
from web_service.utils.get_contexts import (
    get_logged_user_context, get_profile_page_context, get_user_from_context
)

router = APIRouter(tags=['web', 'profile'])


# TODO привести к единому АПИ
# TODO после изменения телефона отсылать потдверждение?
# TODO сделать отписку ?


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
@router.get("/entry", response_class=HTMLResponse)
async def profile(
        context: dict = Depends(get_profile_page_context),
):
    return templates.TemplateResponse(
        "profile.html", context=update_title(context, 'profile.html'))


@router.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile(
        context: dict = Depends(get_logged_user_context),
):
    return templates.TemplateResponse(
        "edit_profile.html", context=update_title(context, "edit_profile.html"))


@router.post("/edit_profile", response_class=HTMLResponse)
async def edit_profile_post(
        username: str = Form(),
        last_name: str = Form(),
        third_name: str = Form(),
        email: EmailStr = Form(),
        phone: str = Form(),
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_from_context)
):

    user.username = username
    user.last_name = last_name
    user.third_name = third_name
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
            context.update(error=f"Неверный адрес почты")
            return templates.TemplateResponse(
                "edit_profile.html", context=update_title(context, "edit_profile"))

    await user.save()
    context.update(user=user, success='Профиль успешно изменен')
    return templates.TemplateResponse("profile.html", context=update_title(context, "profile"))
