from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from schemas.user import UserRegistration
from services.complexes_and_videos import check_level_up
from services.user import (
    register_new_user
)
from web_service.utils import *

router = APIRouter(tags=['web'])

# TODO оплата и сохранение истории платежей - нужен аккаунт +
# TODO Как вычислять сколько осталось до конца комплекса?
# TODO get_logged_user or get_session_user
# TODO хранение просмотренных комплексов и видео, у комплекса должен быть номер


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
        return await login_user(user, request)

    if errors:
        context.update(**errors)
        return templates.TemplateResponse("registration.html", context=context)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='New user registration unrecognized error'
    )


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    if 'token' in request.session:
        request.session.clear()

    return RedirectResponse('/index')


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


@router.post("/entry", response_class=HTMLResponse)
async def entry(
        access_approved: templates.TemplateResponse = Depends(user_entry),
):
    return access_approved


@router.get("/charging", response_class=HTMLResponse)
@router.post("/charging", response_class=HTMLResponse)
async def charging(
        current_complex: Complex = Depends(get_current_user_complex),
        videos: list = Depends(get_complex_videos_list),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    user: User = session_context['user']

    # Calculate video number to next level for current complex
    if videos:
        to_next_level = int((100 - user.progress) / (100 / len(videos)))
        context.update(to_next_level=to_next_level)
    context.update(
        current_complex=current_complex, videos=videos, **session_context
    )
    return templates.TemplateResponse("videos_list.html", context=context)


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


@router.get("/entry_sms", response_class=HTMLResponse)
async def entry_sms(
        context: dict = Depends(get_context),
):
    return templates.TemplateResponse("entry_sms.html", context=context)


@router.post("/entry_sms", response_class=HTMLResponse)
async def entry_sms(
        enter_by_sms: templates.TemplateResponse = Depends(enter_by_sms),
):
    return enter_by_sms


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


@router.get("/complexes_list", response_class=HTMLResponse)
async def complexes_list(
        current_complex: Complex = Depends(get_current_user_complex),
        videos: list = Depends(get_complex_videos_list),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    print(current_complex)
    return templates.TemplateResponse("videos_list.html", context=context)


@router.post("/finishCharging", response_class=HTMLResponse)
async def finishCharging(
        current_complex: Complex = Depends(get_current_user_complex),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session)
):
    old_user_level = user.level
    new_user: User = await check_level_up(user=user, session=session)
    context.update(**session_context, current_complex=current_complex)
    if new_user.level <= old_user_level:
        return RedirectResponse("/charging")
    current_complex: Complex = await Complex.get_by_id(session, user.current_complex)
    context.update(user=new_user, current_complex=current_complex)
    return templates.TemplateResponse("new_level.html", context=context)



