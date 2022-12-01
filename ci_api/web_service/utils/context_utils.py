import secrets
from pathlib import Path

from fastapi import Depends, HTTPException, status, Form
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import MAX_LEVEL, settings, templates, logger
from database.db import get_db_session
from models.models import User, Video, Complex
from schemas.user import UserLogin
from services.depends import get_context_with_request
from services.emails import EmailException, send_email_message
from services.user import user_login, get_bearer_header


COMPANY_PHONE = "9213336698"


def represent_phone(phone: str) -> str:
    return f"8 ({phone[:3]}) {phone[3:6]}-{phone[6:]}"


def get_context(
        context: dict = Depends(get_context_with_request)
) -> dict:
    context.update({
        'email_pattern': r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b",
        "title": "Добро пожаловать",
        "head_title": "Добро пожаловать",
        "icon_link": "/index",
        "company_email": "company@email.com",
        "company_phone": f"tel:{COMPANY_PHONE}",
        "company_represent_phone": f"tel: {represent_phone(COMPANY_PHONE)}",
        "google_play_link": "https://www.google.com",
        "app_store_link": "https://www.apple.com",
        "vk_link": "https://vk.com/cigun_energy",
        "youtube_link": "https://www.youtube.com/channel/UCA3VIncMlr7MxXY2Z_QEM-Q",
        "subscribe_info": "#",
        "conditions": "/user_agree",
        "confidence": "/confidential",
        "feedback_link": "/feedback",
        "help_link": "/help_page"
    })

    return context


def get_profile_context(
        common_context=Depends(get_context)
) -> dict:
    common_context.update(
        {
            "max_level": MAX_LEVEL,
            "title": "Профиль",
            "head_title": "Личный кабинет"
        }
    )
    return common_context


async def get_session_token(request: Request) -> str:
    return request.session.get('token', '')


async def get_session_user(
        token: str = Depends(get_session_token),
        session: AsyncSession = Depends(get_db_session)
) -> User:
    if token:
        return await User.get_by_token(session, token)


async def get_session_context(
        user: User = Depends(get_session_user)
) -> dict:
    """Returns default page context and user data"""
    context = {}
    if user:
        context.update({
            "user": user,
            "user_present_phone": represent_phone(user.phone)
        })

    return context


async def get_user_context(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_context)
) -> dict:
    context.update(**session_context)
    return context


async def get_current_user_complex(
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session),
) -> Complex:
    if user:
        return await Complex.get_by_id(session, user.current_complex)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Complex not found'
    )


async def get_complex_videos_list(
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session),
) -> list[Video]:
    if user:
        return await Video.get_all_by_complex_id(session, user.current_complex)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User not found'
    )


async def get_session_video_by_id(
        video_id: int,
        session: AsyncSession = Depends(get_db_session),
) -> Video:
    if video_id:
        return await Video.get_by_id(session, video_id)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Video not found'
    )


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
        session: AsyncSession = Depends(get_db_session),
        context: dict = Depends(get_profile_context),
        form_data: UserLogin = Depends(UserLogin.as_form)

) -> templates.TemplateResponse:
    if user := await user_login(session, form_data):
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


def generate_random_password() -> str:
    return secrets.token_hex(8)


async def get_email_send_context(email: EmailStr, message: str) -> dict:
    context = {}
    try:
        await send_email_message(email, message)
    except EmailException:
        context.update(error=f"Неверный адрес почты")

    return context


async def restore_password(
        context: dict = Depends(get_context),
        email: EmailStr = Form(...),
        session: AsyncSession = Depends(get_db_session)
):
    user: User = await User.get_by_email(session, email)
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
    await user.save(session)
    context.update(success=f"Новый пароль выслан на почту {user.email}")
    return templates.TemplateResponse("entry.html", context=context)


async def set_new_password(
        context: dict = Depends(get_profile_context),
        session_context: dict = Depends(get_session_context),
        old_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...),
        session: AsyncSession = Depends(get_db_session),
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
    await user.save(session)

    return templates.TemplateResponse("profile.html", context=context)


async def login_user(user, request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/entry', headers=headers)
