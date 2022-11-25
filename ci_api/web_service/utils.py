from pathlib import Path

import pydantic
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import logger, MAX_LEVEL, settings, templates
from database.db import get_db_session
from models.models import User, Video, Complex
from schemas.user import UserRegistration
from services.user import user_login, get_login_token, get_bearer_header, get_user_by_token, \
    validate_logged_user_data


async def validate_register_form(
        form: FormData
) -> tuple[UserRegistration | None, dict]:
    try:
        user_data = UserRegistration(
            username=form['username'],
            last_name=form['last_name'],
            third_name=form['third_name'],
            phone=form['user_phone'],
            email=form['user_email'],
            password=form['password'],
            password2=form['password2'],
            gender=True if form['gender'] == 'male' else False,
            rate_id=1
        )

        return user_data, {}
    except pydantic.error_wrappers.ValidationError as err:
        logger.debug(err)
        error_text: str = err.errors()[0]['loc'][0]
        text = f'Invalid {error_text}'
        return None, {'error': text}


def get_context(request: Request) -> dict:
    return {
        'request': request,
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
        "feedback_link": "/feedback",
        "help_link": "/help_page"
    }


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
        return await get_user_by_token(session, token)


async def get_session_context(
        user: User = Depends(get_session_user)
) -> dict:
    context = {}
    if user:
        context.update({
            "username": user.username,
            "last_name": user.last_name,
            "user_phone": user.phone,
            "user_email": user.email,
            "level": user.level,
            "subscribe_day": user.expired_at
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
):
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

) -> templates.TemplateResponse:

    form: FormData = await request.form()
    user_data, errors = await validate_logged_user_data(form)
    if not user_data and errors:
        context.update(**errors)
        logger.info(f'Login validation error: {errors["error"]}')

        return templates.TemplateResponse("entry.html", context=context)

    if user := await user_login(session, user_data):
        login_token: str = get_login_token(user.id)
        headers: dict[str, str] = get_bearer_header(login_token)
        request.session.update(token=login_token)

        return RedirectResponse('/profile', headers=headers)

    errors = {'error': "Invalid user or password"}
    context.update(**errors)

    return templates.TemplateResponse("entry.html", context=context)

#
# async def load_page(
#         request: Request,
#         session_context: dict = Depends(get_session_context)
# ):
#     page_name: str = str(request.url).split('/')[-1] + '.html'
#     if not session_context:
#         return templates.TemplateResponse("entry.html", context=context)
#     context.update(**session_context)
#     return templates.TemplateResponse(page_name, context=context)
