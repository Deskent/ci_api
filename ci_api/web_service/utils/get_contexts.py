from fastapi import Depends
from pydantic import EmailStr
from starlette.requests import Request

from config import MAX_LEVEL
from exc.exceptions import UserNotLoggedError, ComeTomorrowException
from models.models import User
from services.depends import get_context_with_request
from services.emails import send_email_message, EmailException
from services.utils import represent_phone


COMPANY_PHONE = "9213336698"
DEFAULT_CONTEXT = {
    'email_pattern': r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b",
    "icon_link": "/index",
    "company_email": "company@email.com",
    "company_phone": f"tel:{COMPANY_PHONE}",
    "company_represent_phone": f"tel: {represent_phone(COMPANY_PHONE)}",
    "google_play_link": "https://www.google.com",
    "app_store_link": "https://www.apple.com",
    "vk_link": "https://vk.com/cigun_energy",
    "youtube_link": "https://www.youtube.com/channel/UCA3VIncMlr7MxXY2Z_QEM-Q",
    "subscribe_info": "/subscribe",
    "conditions": "/user_agree",
    "confidence": "/confidential",
    "feedback_link": "/feedback",
    "help_link": "/help_page"
}


async def get_session_token(request: Request) -> str:
    return request.session.get('token', '')


async def get_session_user(
        token: str = Depends(get_session_token),
) -> User:
    if token:
        return await User.get_by_token(token)


def get_base_context(
        context: dict = Depends(get_context_with_request)
) -> dict:
    context.update(DEFAULT_CONTEXT)

    return context


async def get_logged_user_context(
        user: User = Depends(get_session_user),
        context: dict = Depends(get_base_context)
) -> dict:

    if not user:
        raise UserNotLoggedError

    context.update({
        "user": user,
        "user_present_phone": represent_phone(user.phone)
    })

    return context



def get_user_from_context(
        context: dict = Depends(get_logged_user_context)
) -> User:
    return context['user']

async def get_active_user_context(
        user: User = Depends(get_user_from_context),
        context: dict = Depends(get_logged_user_context)
):
    # TODO прописать во всех ендпоинтах
    if user.is_active:
        return context
    raise ComeTomorrowException


def get_profile_page_context(
        context: dict = Depends(get_logged_user_context)
) -> dict:
    context.update(max_level=MAX_LEVEL)
    return context


async def get_email_send_context(email: EmailStr, message: str) -> dict:
    context = {}
    try:
        await send_email_message(email, message)
    except EmailException:
        context.update(error=f"Неверный адрес почты")

    return context