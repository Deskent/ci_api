from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from models.models import Notification
from services.emails import send_verification_mail, EmailException
from web_service.utils import *
from web_service.utils.title_context_func import update_context_title
from web_service.utils.titles_context import get_full_context

router = APIRouter(tags=['web', 'profile'])


# TODO привести к единому АПИ
# TODO после изменения телефона отсылать потдверждение?

# TODO сделать отписку


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
@router.get("/entry", response_class=HTMLResponse)
async def profile(
        context: dict = Depends(get_full_context),
):
    if not context.get('user'):
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, 'entry.html'))
    return templates.TemplateResponse(
        "profile.html", context=update_context_title(context, 'profile.html'))


@router.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile(
        context: dict = Depends(get_full_context),
):
    if not (user := context.get('user')):
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, 'entry'))

    return templates.TemplateResponse(
        "edit_profile.html", context=update_context_title(context, "edit_profile.html"))


@router.post("/edit_profile", response_class=HTMLResponse)
async def edit_profile_post(
        username: str = Form(),
        last_name: str = Form(),
        third_name: str = Form(),
        email: str = Form(),
        phone: str = Form(),
        context: dict = Depends(get_full_context),
):
    if not (user := context.get('user')):
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, 'entry'))
    user.username = username
    user.last_name = last_name
    user.third_name = third_name
    if user.phone != phone:
        # TODO send sms to verify ?
        pass
    user.phone = phone
    if user.email != email:
        try:
            code: str = await send_verification_mail(user)
            user.email_code = code
            user.is_verified = False
            user.email = email
        except EmailException:
            context.update(error=f"Неверный адрес почты")
            return templates.TemplateResponse(
                "edit_profile.html", context=update_context_title(context, "edit_profile"))

    await user.save()
    context.update(user=user, success='Профиль успешно изменен')
    return templates.TemplateResponse("profile.html", context=update_context_title(context, "profile"))


@router.get("/notifications", response_class=HTMLResponse)
async def subscribe(
        context: dict = Depends(get_full_context),
):
    if not (user := context.get('user')):
        return templates.TemplateResponse(
            "entry.html", context=update_context_title(context, 'entry'))
    notifications: list = await Notification.get_all_by_user_id(user.id)
    context.update(notifications=notifications)

    return templates.TemplateResponse(
        "notifications.html", context=update_context_title(context, "notifications"))
