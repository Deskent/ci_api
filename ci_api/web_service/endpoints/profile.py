from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from web_service.utils import *

router = APIRouter(tags=['web', 'profile'])


# TODO обработать post запрос на страницу edit_profile
# TODO сделать проверку пароля после изменения (что он изменился)
# TODO После смены почты или телефона - отправлять подтверждение
# TODO сделать переход на входе в профиль на страницу подтверждения емэйла если он не подтвержден
# TODO Сделать страницу редактирования профиля
# TODO Сделать страницу с сообщением "Подписка отменена"
# TODO сделать переход со страницы Notifications
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

):
    # TODO реализовать
    pass

