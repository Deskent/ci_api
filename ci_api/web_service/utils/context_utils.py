import secrets
from pathlib import Path

from fastapi import Depends, HTTPException, status, Form, BackgroundTasks
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import MAX_LEVEL, settings, templates
from database.db import get_db_session
from models.models import User, Video, Complex
from schemas.user import UserLogin
from services.depends import get_context_with_request
from services.emails import send_verification_mail
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
        "vk_link": "https://www.vk.com",
        "youtube_link": "https://www.youtube.com",
        "subscribe_info": "#",
        "conditions": "#",
        "confidence": "#",
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
    context = {}
    if user:
        context.update({
            "user": user,
            "user_present_phone": represent_phone(user.phone)
        })

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


async def get_session_video_file_name(
        video: Video = Depends(get_session_video_by_id),
) -> str:
    file_path: Path = settings.MEDIA_DIR / video.file_name
    if file_path.exists():
        return str(video.file_name)

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
        login_token: str = await user.get_user_token()
        headers: dict[str, str] = get_bearer_header(login_token)
        request.session.update(token=login_token)

        return RedirectResponse('/profile', headers=headers)

    errors = "Invalid user or password"
    context.update(error=errors)

    return templates.TemplateResponse("entry.html", context=context)


async def load_self_page(
        request: Request,
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
) -> templates.TemplateResponse:
    page_name: str = request.url.path[1:] + '.html'
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)

    context.update(**session_context)

    return templates.TemplateResponse(page_name, context=context)


def generate_random_password() -> str:
    return secrets.token_hex(8)


async def restore_password(
        tasks: BackgroundTasks,
        context: dict = Depends(get_context),
        email: EmailStr = Form(...),
        session: AsyncSession = Depends(get_db_session)
):
    user: User = await User.get_by_email(session, email)
    if not user:
        context.update(error='Invalid email')
        return templates.TemplateResponse("forget1.html", context=context)

    new_password: str = generate_random_password()
    user.password = await user.get_hashed_password(new_password)
    await user.save(session)
    tasks.add_task(send_verification_mail, user)

    context.update(password_restored=f"Новый пароль выслан на почту {user.email}")

    return templates.TemplateResponse("forget1.html", context=context)


async def set_new_password(
        context: dict = Depends(get_profile_context),
        session_context: dict = Depends(get_session_context),
        new_password: str = Form(...),
        session: AsyncSession = Depends(get_db_session),
):
    user: User = session_context.get('user')
    if not user:
        return templates.TemplateResponse("entry.html", context=context)

    context.update(**session_context, password_chanded="Пароль успешно изменен.")
    user.password = await user.get_hashed_password(new_password)
    await user.save(session)

    return templates.TemplateResponse("profile.html", context=context)


async def login_user(user, request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/profile', headers=headers)


