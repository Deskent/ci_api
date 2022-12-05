from pathlib import Path

from fastapi import Depends, HTTPException, status, Form
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import settings, templates, logger
from exc.payment.exceptions import UserNotFoundError, ComplexNotFoundError, VideoNotFoundError
from models.models import User, Video, Complex
from schemas.user import UserLogin
from services.user import user_login, get_bearer_header
from services.utils import generate_random_password
from web_service.utils.titles_context import get_profile_context, \
    get_password_recovery_context, get_session_context, get_email_send_context, get_session_user


async def get_current_user_complex(
        user: User = Depends(get_session_user),
) -> Complex:
    if user:
        return await Complex.get_by_id(user.current_complex)

    raise ComplexNotFoundError


async def get_complex_videos_list(
        user: User = Depends(get_session_user),
) -> list[Video]:
    if user:
        return await Video.get_all_by_complex_id(user.current_complex)

    raise UserNotFoundError


async def get_session_video_by_id(
        video_id: int,
) -> Video:
    if video_id:
        return await Video.get_by_id(video_id)

    raise VideoNotFoundError


async def get_session_video(
        video: Video = Depends(get_session_video_by_id),
) -> Video:
    file_path: Path = settings.MEDIA_DIR / video.file_name
    if file_path.exists():
        return video

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'File {video.file_name} not found'
    )


async def user_entry(
        request: Request,
        context: dict = Depends(get_profile_context),
        form_data: UserLogin = Depends(UserLogin.as_form)

) -> templates.TemplateResponse:
    if user := await user_login(form_data):
        context.update(user=user)
        if not user.is_verified:
            return templates.TemplateResponse("check_email.html", context=context)

        login_token: str = await user.get_user_token()
        headers: dict[str, str] = get_bearer_header(login_token)
        request.session.update(token=login_token)

        return RedirectResponse('/profile', headers=headers)

    error = "Invalid user or password"
    context.update(error=error)

    return templates.TemplateResponse("entry.html", context=context)


async def load_self_page(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
) -> templates.TemplateResponse:
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)

    context.update(**session_context)
    page_name: str = context['request'].url.path[1:] + '.html'

    return templates.TemplateResponse(page_name, context=context)


async def restore_password(
        context: dict = Depends(get_password_recovery_context),
        email: EmailStr = Form(...),
):
    user: User = await User.get_by_email(email)
    if not user:
        context.update(error='Неверный адрес почты')
        return templates.TemplateResponse("forget1.html", context=context)

    new_password: str = generate_random_password()
    email_errors: dict = await get_email_send_context(user.email, new_password)
    if email_errors:
        context.update(email_errors)
        return templates.TemplateResponse("forget1.html", context=context)

    logger.debug(f"New password: {new_password}")
    user.password = await user.get_hashed_password(new_password)
    await user.save()
    context.update(success=f"Новый пароль выслан на почту {user.email}")
    return templates.TemplateResponse("entry.html", context=context)


async def set_new_password(
        context: dict = Depends(get_profile_context),
        session_context: dict = Depends(get_session_context),
        old_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
):
    user: User = session_context.get('user')
    if not user:
        return templates.TemplateResponse("entry.html", context=context)

    context.update(**session_context)
    if not await user.is_password_valid(old_password):
        context.update(error="Неверный пароль")
        return templates.TemplateResponse("edit_profile.html", context=context)

    if password == old_password:
        context.update(error="Новый пароль не должен совпадать со старым")
        return templates.TemplateResponse("edit_profile.html", context=context)

    if password != password2:
        context.update(error="Пароли не совпадают")
        return templates.TemplateResponse("edit_profile.html", context=context)

    context.update(success="Пароль успешно изменен.")
    user.password = await user.get_hashed_password(password)
    await user.save()

    return templates.TemplateResponse("profile.html", context=context)


async def login_user(user, request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/entry', headers=headers)
