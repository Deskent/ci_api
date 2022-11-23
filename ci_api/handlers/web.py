import pydantic
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from database.db import get_session
from schemas.user import UserRegistration, EmailVerify
from services.user import register_new_user, get_login_token, get_bearer_header

router = APIRouter()
templates = Jinja2Templates(directory="static", auto_reload=True)

MAX_LEVEL = 10

context = {
    "max_level": MAX_LEVEL,
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


@router.get("/", response_class=HTMLResponse)
@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    context.update({
        "request": request,
    })
    return templates.TemplateResponse("index.html", context=context)


@router.get("/registration", response_class=HTMLResponse)
async def web_register(request: Request):
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
        session: AsyncSession = Depends(get_session),
):
    context.update({'request': request})
    form = await request.form()
    try:
        EmailVerify(email=form['user_email'])
    except pydantic.error_wrappers.ValidationError:
        errors = {'error': 'Invalid email'}
        context.update(**errors)
        return templates.TemplateResponse("registration.html", context=context)

    gender = True if form['gender'] == 'male' else False
    user_data = UserRegistration(
        username=form['username'],
        last_name=form['last_name'],
        third_name=form['third_name'],
        phone=form['user_phone'],
        email=form['user_email'],
        password=form['password'],
        password2=form['password2'],
        gender=gender,
        rate_id=1
    )
    user, errors = await register_new_user(session, user_data, tasks)
    if user:
        login_token: str = get_login_token(user.id)
        headers: dict[str, str] = get_bearer_header(login_token)
        return RedirectResponse('/profile', headers=headers)

    context.update(**errors)
    return templates.TemplateResponse("registration.html", context=context)


@router.get("/entry", response_class=HTMLResponse)
async def entry(request: Request):
    context.update({
        "request": request,
        "title": "Вход",
        "head_title": "Личный кабинет"
    })
    return templates.TemplateResponse("entry.html", context=context)


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    context.update({
        "request": request,
        "title": "Профиль",
        "head_title": "Личный кабинет"
    })
    return templates.TemplateResponse("profile.html", context=context)


@router.post("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    form = await request.form()
    username = form['username']
    password = form['password']
    user_phone = form.get('user_phone', '000')
    email = form['user_email']
    subscribe_day = 13  # TODO получить из бд
    level = 5  # TODO получить из бд
    context.update({
        "request": request,
        "title": "Профиль",
        "head_title": "Личный кабинет",
        "username": username,
        "last_name": form['last_name'],
        "password": password,
        "user_phone": user_phone,
        "user_email": email,
        "level": level,
        "subscribe_day": subscribe_day
    })
    return templates.TemplateResponse("profile.html", context=context)


@router.get("/notifications", response_class=HTMLResponse)
async def notifications(request: Request):
    context.update({
        "request": request,

    })
    return templates.TemplateResponse("notifications.html", context=context)
