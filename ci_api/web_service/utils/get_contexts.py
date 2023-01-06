from datetime import datetime

from fastapi import Depends
from pydantic import EmailStr
from starlette.requests import Request

from config import MAX_LEVEL
from exc.exceptions import UserNotLoggedError, ComeTomorrowException
from database.models import User, Rate, Avatar
from services.constants import DEFAULT_CONTEXT
from services.depends import get_context_with_request
from services.emails import send_email_message, EmailException
from crud_class.crud import CRUD
from services.utils import represent_phone


EMAIL_PATTERN = {'email_pattern': r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b"}


async def get_browser_session_token(request: Request) -> str:
    return request.session.get('token', '')


async def get_session_user(
        token: str = Depends(get_browser_session_token),
) -> User:
    if token:
        return await CRUD.user.get_by_token(token)
    raise UserNotLoggedError


def get_base_context(
        context: dict = Depends(get_context_with_request)
) -> dict:
    context.update(DEFAULT_CONTEXT)
    context.update(EMAIL_PATTERN)

    return context


async def get_logged_user_context(
        user: User = Depends(get_session_user),
        context: dict = Depends(get_base_context)
) -> dict:
    """Return user instance from browser session context"""

    if not user:
        raise UserNotLoggedError
    avatar: Avatar = await CRUD.avatar.get_by_id(user.avatar)
    context.update({
        "avatar": avatar,
        "user": user,
        "user_present_phone": represent_phone(user.phone)
    })

    return context


def get_user_browser_session(
        context: dict = Depends(get_logged_user_context)
) -> User:
    """Return user instance from browser session context"""

    user: User = context['user']
    if user:
        return user
    raise UserNotLoggedError


async def get_active_user_context(
        user: User = Depends(get_user_browser_session),
        context: dict = Depends(get_logged_user_context)
):
    # TODO прописать во всех ендпоинтах где зарядка
    if user.is_active:
        return context
    raise ComeTomorrowException


def present_user_expired_at_day_and_month(date: datetime) -> str:
    return (
        f'Подписка автоматически продлится: {date.strftime("%d-%m")}'
        if date is not None
        else 'Нет подписки'
    )


async def get_profile_page_context(
        context: dict = Depends(get_logged_user_context)
) -> dict:
    """Return context dict with user, avatar, rate, max_level"""

    user: User = context['user']
    if not (avatar := context.get('avatar')):
        avatar: Avatar = await CRUD.avatar.get_by_id(user.avatar)
    user.expired_at = present_user_expired_at_day_and_month(user.expired_at)
    rate: Rate = await CRUD.rate.get_by_id(user.rate_id)
    context.update(max_level=MAX_LEVEL, user=user, rate=rate, avatar=avatar)

    return context


async def get_email_send_context(email: EmailStr, message: str) -> dict:
    context = {}
    try:
        await send_email_message(email, message)
    except EmailException:
        context.update(error="Неверный адрес почты")

    return context


async def update_user_session_token(request: Request, user: User) -> None:
    """Update new user token to request session"""

    if request:
        request.session.clear()
        login_token: str = await CRUD.user.get_user_token(user)
        request.session.update(token=login_token)
