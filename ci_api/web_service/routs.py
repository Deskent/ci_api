from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger, templates
from database.db import get_db_session
from models.models import Complex, Video
from schemas.user import UserRegistration
from services.user import (
    register_new_user, get_login_token, get_bearer_header
)
from web_service.utils import (
    get_session_context, get_complex_videos_list, get_current_user_complex, get_context,
    get_profile_context, get_session_video_file_name, user_entry, load_self_page,
    restore_password, set_new_password
)

router = APIRouter()


# TODO Body and Forms


@router.get("/", response_class=HTMLResponse)
@router.get("/index", response_class=HTMLResponse)
async def index(
        context: dict = Depends(get_context)
):
    return templates.TemplateResponse("index.html", context=context)


@router.get("/registration", response_class=HTMLResponse)
async def web_register(
        context: dict = Depends(get_context)
):
    context.update({
        "title": "Регистрация",
        "head_title": "Регистрация",
        "personal_data": "/personal_data_info"
    })
    return templates.TemplateResponse("registration.html", context=context)


@router.post("/registration", response_class=HTMLResponse)
async def web_register(
        request: Request,
        tasks: BackgroundTasks,
        context: dict = Depends(get_context),
        session: AsyncSession = Depends(get_db_session),
        form_data: UserRegistration = Depends(UserRegistration.as_form)
):
    if not form_data:
        errors = {'error': 'Пароли не совпадают'}
        context.update(**errors)
        logger.info(f'Field validation error: {errors["error"]}')

        return templates.TemplateResponse("registration.html", context=context)

    user, errors = await register_new_user(session, form_data, tasks)
    if user:
        login_token: str = get_login_token(user.id)
        headers: dict[str, str] = get_bearer_header(login_token)
        request.session.update(token=login_token)

        return RedirectResponse('/profile', headers=headers)

    if errors:
        context.update(**errors)
        return templates.TemplateResponse("registration.html", context=context)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='New user registration unrecognized error'
    )


@router.post("/entry", response_class=HTMLResponse)
async def entry(
        access_approved: templates.TemplateResponse = Depends(user_entry),
):
    return access_approved


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    if 'token' in request.session:
        request.session.clear()

    return RedirectResponse('/index')


@router.get("/entry", response_class=HTMLResponse)
@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
async def profile(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(**session_context)
    return templates.TemplateResponse("profile.html", context=context)


@router.get("/charging", response_class=HTMLResponse)
async def charging(
        current_complex: Complex = Depends(get_current_user_complex),
        videos: list = Depends(get_complex_videos_list),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(
        current_complex=current_complex, videos=videos, **session_context
    )
    return templates.TemplateResponse("charging.html", context=context)


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(**session_context)
    return templates.TemplateResponse("subscribe.html", context=context)


@router.get("/startCharging/{video_id}", response_class=HTMLResponse)
async def start_charging(
        file_name: Video = Depends(get_session_video_file_name),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context)
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(file_name=file_name, **session_context)
    return templates.TemplateResponse("startCharging.html", context=context)


@router.get("/notifications", response_class=HTMLResponse)
@router.get("/feedback", response_class=HTMLResponse)
@router.get("/help_page", response_class=HTMLResponse)
async def help_page(
        self_page: dict = Depends(load_self_page),
):
    return self_page


@router.get("/forget1", response_class=HTMLResponse)
async def forget1(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("forget1.html", context=context)


@router.post("/forget1", response_class=HTMLResponse)
async def forget1(
        restore_password: dict = Depends(restore_password),
):
    return restore_password


@router.get("/newPassword", response_class=HTMLResponse)
async def newPassword(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("newPassword.html", context=context)


@router.post("/newPassword", response_class=HTMLResponse)
async def newPassword(
        set_new_password: dict = Depends(set_new_password),
):
    return set_new_password
