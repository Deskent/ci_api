from fastapi import Depends
from pydantic import EmailStr
from starlette.requests import Request

from config import MAX_LEVEL
from models.models import User
from services.depends import get_context_with_request
from services.emails import send_email_message, EmailException
from services.utils import represent_phone
from web_service.utils.title_context_func import update_title


async def get_session_token(request: Request) -> str:
    return request.session.get('token', '')


async def get_session_user(
        token: str = Depends(get_session_token),
) -> User:
    if token:
        return await User.get_by_token(token)


COMPANY_PHONE = "9213336698"


def get_context(
        context: dict = Depends(get_context_with_request)
) -> dict:
    context.update({
        'email_pattern': r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b",
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
    common_context.update(max_level=MAX_LEVEL)
    return update_title(common_context, key="profile")


def get_sms_recovery_context(
        common_context=Depends(get_context)
) -> dict:
    return update_title(common_context, key="sms_recovery")


def get_email_check_context(
        common_context=Depends(get_profile_context)
) -> dict:
    return update_title(common_context, key="check_email_code")


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


async def get_full_context(
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_context)
) -> dict:
    context.update(**session_context)
    return context


async def get_email_send_context(email: EmailStr, message: str) -> dict:
    context = {}
    try:
        await send_email_message(email, message)
    except EmailException:
        context.update(error=f"Неверный адрес почты")

    return context
