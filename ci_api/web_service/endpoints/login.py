from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from schemas.user import UserRegistration
from services.user import register_new_user
from web_service.utils import *

router = APIRouter(tags=['web', 'login'])


@router.get("/", response_class=HTMLResponse)
@router.get("/index", response_class=HTMLResponse)
async def index(
        context: dict = Depends(get_context)
):
    return templates.TemplateResponse("index.html", context=context)


@router.get("/user_agree", response_class=HTMLResponse)
async def user_agree(
        context: dict = Depends(get_context)
):
    context.update(
        title='Пользовательское соглашение',
        head_title='Пользовательское соглашение'
    )

    return templates.TemplateResponse('user_agree.html', context=context)


@router.get("/confidential", response_class=HTMLResponse)
async def confidential(
        context: dict = Depends(get_context)
):
    context.update(
        title='Политика',
        head_title='Политика в отношении обработки персональных данных'
    )

    return templates.TemplateResponse('confidential.html', context=context)


@router.post("/registration", response_class=HTMLResponse)
async def web_register_post(
        request: Request,
        context: dict = Depends(get_context),
        form_data: UserRegistration = Depends(UserRegistration.as_form)
):
    if not form_data:
        errors = {'error': 'Пароли не совпадают'}
        context.update(**errors)
        logger.info(f'Field validation error: {errors["error"]}')

        return templates.TemplateResponse("registration.html", context=context)

    user, errors = await register_new_user(form_data)
    if user:
        return await login_user(user, request)

    if errors:
        context.update(**errors)
        return templates.TemplateResponse("registration.html", context=context)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='New user registration unrecognized error'
    )


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


@router.post("/newPassword", response_class=HTMLResponse)
async def newPassword(
        set_new_password: dict = Depends(set_new_password),
):
    return set_new_password


@router.get("/entry_sms", response_class=HTMLResponse)
async def entry_sms(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("entry_sms.html", context=context)


@router.post("/entry_sms", response_class=HTMLResponse)
async def entry_sms_posts(
        enter_by_sms: templates.TemplateResponse = Depends(enter_by_sms),
):
    return enter_by_sms


@router.get("/forget1", response_class=HTMLResponse)
async def forget1(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("forget1.html", context=context)


@router.post("/forget1", response_class=HTMLResponse)
async def forget1_post(
        restore_password: dict = Depends(restore_password),
):
    return restore_password


@router.get("/forget2", response_class=HTMLResponse)
async def forget2(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("forget2.html", context=context)


@router.post("/forget2", response_class=HTMLResponse)
@router.post("/forget3", response_class=HTMLResponse)
async def login_with_sms(
        check_sms_code: dict = Depends(approve_sms_code),
):
    return check_sms_code


@router.get("/forget3", response_class=HTMLResponse)
async def forget3(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("forget3.html", context=context)


@router.get("/check_email", response_class=HTMLResponse)
@router.post("/check_email", response_class=HTMLResponse)
async def check_email(
        context: dict = Depends(get_profile_context),
        email: EmailStr = Form(...),
        email_token: str = Form(...)
):
    user: User = await User.get_by_email(email)
    if not user:
        error = 'Пользователь не найден'
        context.update(error=error)
        return templates.TemplateResponse("index.html", context=context)

    if user.email_code != email_token:
        error = 'Введен неверный токен'
        context.update(error=error)
        return templates.TemplateResponse("check_email.html", context=context)

    if not user.is_verified:
        user.is_verified = True
        await user.save()

    session_context: dict = await get_session_context(user)
    context.update(success='Аккаунт верифицирован', **session_context)

    return templates.TemplateResponse("profile.html", context=context)
