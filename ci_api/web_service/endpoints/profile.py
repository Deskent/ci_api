from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.emails import send_verification_mail
from web_service.utils import *

router = APIRouter(tags=['web', 'profile'])


# TODO сделать обработку Notifications
# TODO после изменения телефона отсылать потдверждение?

# TODO оплата и сохранение истории платежей - нужен аккаунт +
# TODO get_logged_user or get_session_user


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
@router.get("/entry", response_class=HTMLResponse)
async def profile(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(**session_context)
    return templates.TemplateResponse("profile.html", context=context)


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(**session_context)
    return templates.TemplateResponse("subscribe.html", context=context)


@router.get("/edit_profile", response_class=HTMLResponse)
@router.get("/cancel_subscribe", response_class=HTMLResponse)
@router.get("/notifications", response_class=HTMLResponse)
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
        session: AsyncSession = Depends(get_db_session)
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
        except EmailException:
            context.update(error=f"Неверный адрес почты")
            return templates.TemplateResponse("edit_profile.html", context=context)
    user.email = email
    user.is_verified = False

    await user.save(session)
    session_context.update(user=user, success='Профиль успешно изменен')
    context.update(**session_context)

    return templates.TemplateResponse("profile.html", context=context)
