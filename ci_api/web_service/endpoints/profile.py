from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from models.models import Notification
from services.emails import send_verification_mail, EmailException
from web_service.utils import *

router = APIRouter(tags=['web', 'profile'])


# TODO привести к единому АПИ
# TODO после изменения телефона отсылать потдверждение?

# TODO сделать отписку


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
@router.get("/entry", response_class=HTMLResponse)
async def profile(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        context.update(head_title="Добро пожаловать")
        return templates.TemplateResponse("entry.html", context=context)
    context.update(**session_context)
    context.update(head_title="Профиль")
    return templates.TemplateResponse("profile.html", context=context)


@router.get("/edit_profile", response_class=HTMLResponse)
@router.get("/feedback", response_class=HTMLResponse)
@router.get("/help_page", response_class=HTMLResponse)
async def help_page(
        self_page: dict = Depends(load_self_page),
):
    return self_page


@router.post("/edit_profile", response_class=HTMLResponse)
async def edit_profile_post(
        username: str = Form(),
        last_name: str = Form(),
        third_name: str = Form(),
        email: str = Form(),
        phone: str = Form(),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    user: User = session_context['user']
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
            context.update(head_title="Редактирование профиля")
            return templates.TemplateResponse("edit_profile.html", context=context)

    await user.save()
    session_context.update(user=user, success='Профиль успешно изменен')
    context.update(**session_context)
    context.update(head_title="Редактирование профиля")
    return templates.TemplateResponse("profile.html", context=context)


@router.get("/notifications", response_class=HTMLResponse)
async def subscribe(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),

):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    user: User = session_context['user']
    notifications: list = await Notification.get_all_by_user_id(user.id)
    context.update(**session_context, notifications=notifications)
    context.update(head_title="Уведомления")

    return templates.TemplateResponse("notifications.html", context=context)
