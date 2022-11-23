from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData

from config import logger
from database.db import get_session
from services.user import (
    register_new_user, get_login_token, get_bearer_header, validate_register_form,
    EntryProfile
)

router = APIRouter()
templates = Jinja2Templates(directory="static", auto_reload=True)

MAX_LEVEL = 10


def get_context() -> dict:
    return {
        "title": "Добро пожаловать",
        "head_title": "Добро пожаловать",
        "icon_link": "/index",
        "company_email": "company@email.com",
        "phone": "tel:89999999998",
        "google_play_link": "https://www.google.com",
        "app_store_link": "https://www.apple.com",
        "vk_link": "https://www.vk.com",
        "youtube_link": "https://www.youtube.com",
        "subscribe_info": "#",
        "conditions": "#",
        "confidence": "#",
        "feedback_link": "#",
        "help_link": "#"
    }


def get_profile_context() -> dict:
    common_context = get_context()
    common_context.update(
        {
            "max_level": MAX_LEVEL,
        }
    )
    return common_context


@router.get("/", response_class=HTMLResponse)
@router.get("/index", response_class=HTMLResponse)
async def index(
        request: Request,
        context: dict = Depends(get_context)
):
    context.update({
        "request": request,
    })
    return templates.TemplateResponse("index.html", context=context)


@router.get("/registration", response_class=HTMLResponse)
async def web_register(
        request: Request,
        context: dict = Depends(get_context)
):
    context.update({
        "request": request,
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
        session: AsyncSession = Depends(get_session),
):
    context.update({'request': request})
    form: FormData = await request.form()
    user_data, errors = await validate_register_form(form)
    if not user_data and errors:
        context.update(**errors)
        logger.info(f'Email validation error: {errors["text"]}')

        return templates.TemplateResponse("registration.html", context=context)

    user, errors = await register_new_user(session, user_data, tasks)
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


@router.get("/entry", response_class=HTMLResponse)
async def entry(
        request: Request,
        session: AsyncSession = Depends(get_session),
        context: dict = Depends(get_context),
):
    redirect = EntryProfile(request, context, session, templates)
    return await redirect.enter_profile()


@router.post("/entry", response_class=HTMLResponse)
async def entry(
        request: Request,
        session: AsyncSession = Depends(get_session),
        context: dict = Depends(get_context),
):
    redirect = EntryProfile(request, context, session, templates)

    return await redirect.user_entry()


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    if 'token' in request.session:
        request.session.clear()

    return RedirectResponse('/entry')


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
async def profile(
        request: Request,
        context: dict = Depends(get_profile_context),
        session: AsyncSession = Depends(get_session),
):
    return await EntryProfile(request, context, session, templates).enter_profile()


@router.get("/notifications", response_class=HTMLResponse)
async def notifications(
        request: Request,
        context: dict = Depends(get_context),
):
    context.update({
        "request": request,
    })
    return templates.TemplateResponse("notifications.html", context=context)
