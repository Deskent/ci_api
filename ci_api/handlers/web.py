from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="static", auto_reload=True)

context = {
    "title": "Добро пожаловать",
    "head_title": "Добро пожаловать",
    "icon_link": "/index",
    "email": "company@email.com",
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


@router.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    context.update({
        "request": request,
    })
    return templates.TemplateResponse("index.html", context=context)


@router.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse('/index')


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
async def web_register(request: Request):
    # TODO выковырять gender из джаваскрипта
    form = await request.form()
    username = form['username']
    password = form['password']
    phone = form['phone']
    gender = form['gender']
    # TODO Провалидировать данные
    print(form)

    return RedirectResponse('/profile')


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
    phone = form['phone']
    subscribe_day = 13
    level = 5
    context.update({
        "request": request,
        "title": "Профиль",
        "head_title": "Личный кабинет",
        "username": username,
        "user_phone": phone,
        "level": level,
        "subscribe_day": subscribe_day
    })
    return templates.TemplateResponse("profile.html", context=context)
